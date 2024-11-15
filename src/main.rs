use algorithm::LocalSearch;
use eframe::egui;
use egui::{pos2, vec2, Color32, Rect, ScrollArea, TextStyle};
use problem::{Problem, ProblemRectangle};

mod problem;
mod algorithm;

use crate::algorithm::OptimizationAlgorithm;


const SCALE_FACTOR: f32 = 10.0;
const BOX_SPACING: f32 = 10.0;

fn main() -> eframe::Result {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default().with_inner_size([800.0, 800.0]),
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
    opt_algo: LocalSearch
}



impl MainApp {
    fn new(_cc: &eframe::CreationContext<'_>) -> Self {
        // TODO: move this
        let my_problem = Problem::new(10, 35, 1..5, 2..8);
        MainApp {
            opt_algo: LocalSearch::init(my_problem)
        }
    }

    fn draw_current_solution(&self, ui: &mut egui::Ui) {
        let current_solution = self.opt_algo.get_current_solution();
        
        let painter = ui.painter();

        let boxes_per_row = ((current_solution.boxes.len() as f64).sqrt() as i64 + 1) as usize;

        for (box_num, problem_box) in current_solution.boxes.iter().enumerate() {
            let box_row = box_num % boxes_per_row;
            let box_idx_in_row = box_num / boxes_per_row;

            let box_origin = egui::Pos2 {
                x: box_idx_in_row as f32 * (problem_box.side_length as f32 + BOX_SPACING) * SCALE_FACTOR,
                y: box_row as f32 * (problem_box.side_length as f32 + BOX_SPACING) * SCALE_FACTOR
            };
            let box_size = egui::Vec2 {
                x: problem_box.side_length as f32 * SCALE_FACTOR,
                y: problem_box.side_length as f32 * SCALE_FACTOR
            };
            let box_rect = Rect::from_min_size(box_origin, box_size);
            painter.rect_filled(box_rect, 0.0, Color32::from_rgb(255, 255, 255));

            // Also paint the box's rectangles
            for problem_rectangle in problem_box.rectangles.iter() {
                let rect_origin: egui::Pos2 = box_origin + (egui::Vec2::from(problem_rectangle.get_origin()) * SCALE_FACTOR);
                let rect_size: egui::Vec2 = egui::Vec2::from(problem_rectangle.get_size()) * SCALE_FACTOR;

                let rect_rect = Rect::from_min_size(rect_origin, rect_size);
                painter.rect_filled(rect_rect, 0.0, Color32::from_rgb(255, 0, 0));   
            }
        }
    }
}

impl eframe::App for MainApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {

        egui::CentralPanel::default().show(ctx, |ui| {
            egui::TopBottomPanel::top("top_panel")
                .min_height(32.0)
                .show_inside(ui, |ui| {
                if ui.button("Tick").clicked() {
                    self.opt_algo.tick();
                }
            });
            // TODO: put this in a separate panel or something
            egui::CentralPanel::default()
                .show_inside(ui, |ui| {
                self.draw_current_solution(ui);
            });
        });
    }
}