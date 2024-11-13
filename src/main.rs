#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")] // hide console window on Windows in release

use eframe::egui;

fn main() -> eframe::Result {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([320.0, 240.0]),
        ..Default::default()
    };
    eframe::run_native(
        "Optalgo Programmierprojekt",
        options,
        Box::new(|cc| {
            Ok(Box::new(MainApp::new(cc)))
        }),
    )
}

struct MainApp {
    some_text: String
}

impl Default for MainApp {
    fn default() -> Self {
        Self {
            some_text: "Hello haha".to_owned()
        }
    }
}

impl MainApp {
    fn new(cc: &eframe::CreationContext<'_>) -> Self {
        Self::default()
    }
}

impl eframe::App for MainApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("A heading");

            
            ui.label(format!("The text: '{}'", self.some_text));
        });
    }
}