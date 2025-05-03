from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, ttk
import os

class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Grid Slicer")
        
        # Grid dimensions mapping
        self.grid_dimensions = {
            "1x3": (3112, 1350),
            "2x3": (3112, 2702),
            "3x3": (3112, 4054)
        }
        
        # Initialize variables
        self.original_image = None
        self.resized_image = None
        self.photo = None
        self.drag_start_y = None
        self.current_y_offset = 0
        self.canvas_width = 800  # Scaled display width
        self.canvas_height = 1000  # Increased display height
        self.display_width = 0
        self.display_height = 0
        self.bg_color = 'black'  # Default background color
        self.grid_type = "1x3"   # Default grid type
        
        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(expand=True, fill='both')
        
        # Create canvas (without scrollbar)
        self.canvas = tk.Canvas(main_frame, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(expand=True, fill='both')
        
        # Create control frame
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)
        # Create button frame for horizontal alignment
        button_frame = tk.Frame(control_frame)
        button_frame.pack()
        
        # 1. Select Image button
        self.select_button = tk.Button(button_frame, text="Select Image", 
                                     command=self.select_image)
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        # 2. Grid type selection
        grid_frame = tk.Frame(button_frame)
        grid_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(grid_frame, text="Grid:").pack(side=tk.LEFT)
        self.grid_var = tk.StringVar(value='1x3')
        grid_combo = ttk.Combobox(grid_frame, textvariable=self.grid_var, 
                                 values=['1x3', '2x3', '3x3'], width=8)
        grid_combo.pack(side=tk.LEFT, padx=5)
        grid_combo.bind('<<ComboboxSelected>>', self.update_grid_type)
        
        # 3. Scale mode selection (initially hidden)
        self.scale_frame = tk.Frame(button_frame)
        self.scale_var = tk.StringVar(value='fit')
        self.fit_radio = tk.Radiobutton(self.scale_frame, text="Fit", 
                                      variable=self.scale_var, value="fit",
                                      command=self.update_scale_mode)
        self.fill_radio = tk.Radiobutton(self.scale_frame, text="Fill", 
                                       variable=self.scale_var, value="fill",
                                       command=self.update_scale_mode)
        self.fit_radio.pack(side=tk.LEFT)
        self.fill_radio.pack(side=tk.LEFT)
        
        # 4. Background color selection
        bg_frame = tk.Frame(button_frame)
        bg_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Label(bg_frame, text="Background:").pack(side=tk.LEFT)
        self.bg_var = tk.StringVar(value='black')
        bg_combo = ttk.Combobox(bg_frame, textvariable=self.bg_var, 
                               values=['black', 'white', 'gray'], width=8)
        bg_combo.pack(side=tk.LEFT, padx=5)
        bg_combo.bind('<<ComboboxSelected>>', self.update_background)
        
        # 5. Slice button
        self.crop_button = tk.Button(button_frame, text="Slice", 
                                   command=self.perform_crop, state='disabled')
        self.crop_button.pack(side=tk.LEFT, padx=5)
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.canvas.bind('<ButtonRelease-1>', self.stop_drag)

    def update_grid_type(self, event=None):
        self.grid_type = self.grid_var.get()
        
        # Show/hide scale mode selection for 2x3 and 3x3 grid
        if self.grid_type in ["2x3", "3x3"]:
            self.scale_frame.pack(side=tk.LEFT, padx=10)
            # Set default to 'fill' when switching to 2x3 or 3x3
            self.scale_var.set('fill')
        else:
            self.scale_frame.pack_forget()
        
        if hasattr(self, 'original_image') and self.original_image is not None:
            self.process_image()

    def update_scale_mode(self):
        if hasattr(self, 'original_image') and self.original_image is not None:
            self.process_image()

    def update_background(self, event=None):
        self.bg_color = self.bg_var.get()
        if hasattr(self, 'resized_image'):
            self.draw_interface()

    def get_current_dimensions(self):
        return self.grid_dimensions[self.grid_type]

    def resize_maintain_aspect(self, img, target_width, target_height):
        original_width, original_height = img.size
        original_ratio = original_width / original_height
        target_ratio = target_width / target_height

        # For 2x3 and 3x3 grid in "fit" mode, only scale to fit width
        if self.grid_type in ["2x3", "3x3"] and self.scale_var.get() == "fit":
            new_width = target_width
            new_height = int(target_width / original_ratio)
        else:
            if original_ratio > target_ratio:
                new_height = target_height
                new_width = int(new_height * original_ratio)
            else:
                new_width = target_width
                new_height = int(new_width / original_ratio)

        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        paste_x = (target_width - new_width) // 2
        paste_y = (target_height - new_height) // 2
        
        return resized_img, (new_width, new_height), (paste_x, paste_y)

    def process_image(self):
        # Get current dimensions
        target_width, target_height = self.get_current_dimensions()
        
        # Get resized image and dimensions
        self.resized_image, self.real_dims, self.paste_pos = self.resize_maintain_aspect(
            self.original_image, target_width, target_height
        )
        
        # Create display version (scaled down)
        scale_factor = self.canvas_width / target_width
        self.display_width = int(self.real_dims[0] * scale_factor)
        self.display_height = int(self.real_dims[1] * scale_factor)
        
        self.display_image = self.resized_image.resize(
            (self.display_width, self.display_height), 
            Image.Resampling.LANCZOS
        )
        self.photo = ImageTk.PhotoImage(self.display_image)
        
        # Reset offset
        self.current_y_offset = 0
        
        # Draw initial view
        self.draw_interface()
        
        # Automatically confirm initial position
        self.confirm_position()

    def select_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if file_path:
            self.original_image = Image.open(file_path)
            self.process_image()

    def draw_interface(self):
        self.canvas.delete("all")
        
        target_width, target_height = self.get_current_dimensions()
        scale_factor = self.canvas_width / target_width
        frame_height = int(target_height * scale_factor)
        
        # Calculate vertical centering offset
        canvas_center_y = self.canvas_height / 2
        frame_center_y = frame_height / 2
        vertical_offset = int(canvas_center_y - frame_center_y)
        
        # Calculate scaled paste position
        scaled_paste_x = int(self.paste_pos[0] * scale_factor)
        scaled_paste_y = int(self.paste_pos[1] * scale_factor) + self.current_y_offset
        
        # Draw background with selected color
        self.canvas.create_rectangle(0, 0, self.canvas_width, self.canvas_height,
                                   fill=self.bg_color)
        
        # Always use yellow for guide lines
        guide_color = 'yellow'
        
        # Draw the frame outline
        self.canvas.create_rectangle(0, vertical_offset, 
                                   self.canvas_width, frame_height + vertical_offset,
                                   outline=guide_color, width=2)
        
        # Draw the image
        self.canvas.create_image(
            scaled_paste_x + self.display_width // 2,
            scaled_paste_y + self.display_height // 2 + vertical_offset,
            image=self.photo
        )
        
        # Draw guide lines based on grid type
        dash_pattern = (5, 5)  # 5 pixels line, 5 pixels gap
        
        # Always draw vertical guides (all grid types have 3 columns)
        first_third_x = self.canvas_width // 3
        second_third_x = (self.canvas_width * 2) // 3
        
        # Draw vertical guides with horizontal end lines
        for x_pos in [first_third_x, second_third_x]:
            # Vertical line
            self.canvas.create_line(x_pos, vertical_offset, 
                                  x_pos, frame_height + vertical_offset, 
                                  fill=guide_color, dash=dash_pattern)
        
        # Draw horizontal guides based on grid type
        rows = int(self.grid_type[0])  # Get number of rows from grid type
        
        # Always draw top and bottom horizontal lines
        self.canvas.create_line(0, vertical_offset, 
                              self.canvas_width, vertical_offset,
                              fill=guide_color, dash=dash_pattern)
        self.canvas.create_line(0, frame_height + vertical_offset,
                              self.canvas_width, frame_height + vertical_offset,
                              fill=guide_color, dash=dash_pattern)
        
        # Draw additional horizontal guides for 2x3 and 3x3
        if rows > 1:
            for i in range(1, rows):
                y_pos = vertical_offset + (frame_height * i) // rows
                self.canvas.create_line(0, y_pos, self.canvas_width, y_pos, 
                                     fill=guide_color, dash=dash_pattern)

    def start_drag(self, event):
        if self.resized_image:
            self.drag_start_y = event.y

    def drag(self, event):
        if self.drag_start_y is not None and self.resized_image:
            delta_y = event.y - self.drag_start_y
            
            target_width, target_height = self.get_current_dimensions()
            scale_factor = self.canvas_width / target_width
            frame_height = int(target_height * scale_factor)
            
            # Calculate max drag based on image and frame heights
            if self.grid_type in ["2x3", "3x3"] and self.scale_var.get() == "fit":
                # For fit mode, use actual image height
                max_drag = int((self.display_height - frame_height) / 2)
            else:
                # For fill mode and other grid types
                max_drag = int((self.display_height - frame_height) / 2)
            
            # Ensure max_drag is not negative
            max_drag = max(0, max_drag)
            
            new_offset = self.current_y_offset + delta_y
            new_offset = max(-max_drag, min(max_drag, new_offset))
            
            self.current_y_offset = new_offset
            self.draw_interface()
            self.drag_start_y = event.y

    def stop_drag(self, event):
        if self.drag_start_y is not None and self.resized_image:
            self.drag_start_y = None
            self.confirm_position()

    def confirm_position(self):
        if self.resized_image:
            target_width, target_height = self.get_current_dimensions()
            scale_factor = target_width / self.canvas_width
            final_y_offset = int(self.current_y_offset * scale_factor)
            
            final_img = Image.new('RGB', (target_width, target_height), self.bg_color)
            paste_y = self.paste_pos[1] + final_y_offset
            final_img.paste(self.resized_image, (self.paste_pos[0], paste_y))
            
            self.final_image = final_img
            self.crop_button.config(state='normal')

    def perform_crop(self):
        if hasattr(self, 'final_image'):
            slices = []
            x_coords = [(0, 1080), (1016, 2096), (2032, 3112)]
            
            # Determine y coordinates based on grid type
            if self.grid_type == "1x3":
                y_coords = [(0, 1350)]
            elif self.grid_type == "2x3":
                y_coords = [(0, 1350), (1352, 2702)]
            else:  # 3x3
                y_coords = [(0, 1350), (1352, 2702), (2702, 4052)]
            
            for y_start, y_end in y_coords:
                for x_start, x_end in x_coords:
                    slice_img = self.final_image.crop((x_start, y_start, x_end, y_end))
                    slices.append(slice_img)
            
            # Ask for save location
            save_dir = filedialog.askdirectory(title="Select folder to save slices")
            
            if save_dir:
                for i, slice_img in enumerate(slices):
                    save_path = os.path.join(save_dir, f"slice_{i+1}.png")
                    slice_img.save(save_path)
                print("Images saved successfully!")

# Create the main window
root = tk.Tk()
app = ImageCropper(root)
root.mainloop() 