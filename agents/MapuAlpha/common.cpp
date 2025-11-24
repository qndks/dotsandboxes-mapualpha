#include "common.h"
using namespace std;

#define CELL(x, y)                                  \
    XYZ{int8_t(x), int8_t(y), int8_t(0)},           \
        XYZ{int8_t((x) + 1), int8_t(y), int8_t(1)}, \
        XYZ{int8_t(x), int8_t((y) + 1), int8_t(0)}, \
        XYZ { int8_t(x), int8_t(y), int8_t(1) }
#define CELL_ROW(y) \
    CELL(0, y), CELL(1, y), CELL(2, y), CELL(3, y), CELL(4, y)
XYZ eToXYZ[NUM_EDGE] = {
    CELL_ROW(0),
    CELL_ROW(1),
    CELL_ROW(2),
    CELL_ROW(3),
    CELL_ROW(4),
};
#undef CELL_ROW
#undef CELL

Clock::time_point c_startTime;
double g_timeLimitMs = 24000; 
double g_timeLeft = g_timeLimitMs;
double c_timeLimitMs;
bool g_timeUp = false;     
int prev_move_count = 100; 
long long g_nodes = 0;  
array<int8_t, NUM_EDGE> order = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
    20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
    30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
    40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
    50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
    60, 61, 62, 63, 64, 65, 66, 67, 68, 69,
    70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
    80, 81, 82, 83, 84, 85, 86, 87, 88, 89,
    90, 91, 92, 93, 94, 95, 96, 97, 98, 99
};