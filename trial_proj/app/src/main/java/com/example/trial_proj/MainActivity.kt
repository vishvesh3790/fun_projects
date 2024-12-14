package com.example.trial_proj

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    
    private lateinit var btnStart: Button
    private lateinit var btnContinue: Button
    private lateinit var btnPause: Button
    private lateinit var btnEnd: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize buttons
        btnStart = findViewById(R.id.btnStart)
        btnContinue = findViewById(R.id.btnContinue)
        btnPause = findViewById(R.id.btnPause)
        btnEnd = findViewById(R.id.btnEnd)

        // Set click listeners
        btnStart.setOnClickListener {
            showToast("Started")
        }

        btnContinue.setOnClickListener {
            showToast("Continued")
        }

        btnPause.setOnClickListener {
            showToast("Paused")
        }

        btnEnd.setOnClickListener {
            showToast("Ended")
        }
    }

    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
