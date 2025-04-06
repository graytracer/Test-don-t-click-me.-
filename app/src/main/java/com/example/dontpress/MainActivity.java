package com.example.dontpress;

import android.os.Bundle;
import android.os.Handler;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    
    private Button dontPressButton;
    private TextView warningText;
    private Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        dontPressButton = findViewById(R.id.dontPressButton);
        warningText = findViewById(R.id.warningText);
        
        dontPressButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Hide the button and show the warning text
                dontPressButton.setVisibility(View.GONE);
                warningText.setVisibility(View.VISIBLE);
                
                // After 2 seconds, hide the text and show the button again
                handler.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        warningText.setVisibility(View.GONE);
                        dontPressButton.setVisibility(View.VISIBLE);
                    }
                }, 2000); // 2 seconds delay
            }
        });
    }
} 