use algorithm::LocalSearch;
use eframe::egui;
use egui::{pos2, vec2, Color32, Rect, ScrollArea, TextStyle};
use problem::{Problem, ProblemRectangle};

mod problem;
mod algorithm;

use crate::algorithm::OptimizationAlgorithm;

const BOX_SPACING: f32 = 3.0;
const PADDING_X: f32 = 10.0;
const PADDING_Y: f32 = 25.0;

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
        let clip_rect = ui.clip_rect();
        
        let boxes_per_row = ((current_solution.boxes.len() as f64).sqrt() as i64 + 1) as usize;
        let num_rows = current_solution.boxes.len() / boxes_per_row + 1;

        // Calculate x and y scaling factors from clip rect to content size ratio
        // TODO: clean this up
        let box_size = current_solution.boxes.first().unwrap().side_length as f32;
        let scale_x = clip_rect.width() / (boxes_per_row as f32 * (box_size + BOX_SPACING));
        let scale_y = clip_rect.height() / (num_rows as f32 * (box_size + BOX_SPACING));

        for (box_num, problem_box) in current_solution.boxes.iter().enumerate() {
            let box_row = box_num % boxes_per_row;
            let box_idx_in_row = box_num / boxes_per_row;

            let box_origin = egui::Pos2 {
                x: box_idx_in_row as f32 * (problem_box.side_length as f32 + BOX_SPACING) * scale_x + PADDING_X,
                y: box_row as f32 * (problem_box.side_length as f32 + BOX_SPACING) * scale_y + PADDING_Y
            };
            let box_size = egui::Vec2 {
                x: problem_box.side_length as f32 * scale_x,
                y: problem_box.side_length as f32 * scale_y
            };
            let box_rect = Rect::from_min_size(box_origin, box_size);
            painter.rect_filled(box_rect, 0.0, Color32::from_rgb(255, 255, 255));

            // Also paint the box's rectangles
            for problem_rectangle in problem_box.rectangles.iter() {
                let rect_origin: egui::Pos2 = box_origin + (egui::Vec2::from(problem_rectangle.get_origin()) * vec2(scale_x, scale_y));
                let rect_size: egui::Vec2 = egui::Vec2::from(problem_rectangle.get_size()) * vec2(scale_x, scale_y);

                let rect_rect = Rect::from_min_size(rect_origin, rect_size);

                // Decide color on whether this was the last moved rect or not
                let color = if Some(problem_rectangle.get_id()) == current_solution.last_moved_rec_id {                    
                    Color32::from_rgb(255, 0, 0)
                } else {
                    Color32::from_rgb(255, 0, 255)
                };

                painter.rect_filled(rect_rect, 0.0, color);   
            }
        }
    }
}

impl eframe::App for MainApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        egui::TopBottomPanel::top("button_bar").show(ctx, |ui| {
            egui::menu::bar(ui, |ui| {
                if ui.button("Tick").clicked() {
                    self.opt_algo.tick();
                }
            });
        });

        egui::CentralPanel::default().show(ctx, |ui| {
            self.draw_current_solution(ui);
        });
    }
}