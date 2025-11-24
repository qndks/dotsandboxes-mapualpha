#include "common.h"

struct TimeManager {
    double total_time;
    double D0;

    TimeManager(double total_time_sec, double initial_edges, double initial_boxes) : total_time(total_time_sec) {
        D0 = max(1.0, (initial_edges - initial_boxes) / 2.0);
    } 

    double get_time_for_move(double remaining_time, int remaining_edges, int remaining_boxes) {
        double D = max(1.0, (remaining_edges - remaining_boxes) / 2.0); 
        double base = remaining_time / D;
        double progress = 1.0 - D / D0;
        if (progress < 0.0) progress = 0.0;
        if (progress > 1.0) progress = 1.0;
        const double low = 0.03; 
        const double high = 3.0; 
        const double gamma = 2.0; 
        double factor = low + (high - low) * pow(progress, gamma);
        double t_move = base * factor;
        double min_time = 0.001;
        double max_frac = 0.9;  
        if (t_move < min_time) t_move = min_time;
        if (t_move > remaining_time * max_frac) t_move = remaining_time * max_frac;
        return t_move;
    }
};