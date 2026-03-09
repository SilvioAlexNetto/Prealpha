package com.silvionetto.HealthPantry;

import android.os.Bundle;

import com.getcapacitor.BridgeActivity;
import com.capacitorjs.plugins.camera.CameraPlugin;

public class MainActivity extends BridgeActivity {

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        registerPlugin(CameraPlugin.class);
    }
}