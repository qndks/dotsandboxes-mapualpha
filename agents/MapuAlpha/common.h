#ifndef COMMON_H
#define COMMON_H

#include <cstdint> 
#include <chrono>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <random>
#include <array>
#include <cmath>
#include <algorithm>
#include <cstring>
#include <numeric>
#include <iostream>

static constexpr int BOX_X = 5;
static constexpr int BOX_Y = 5;
static constexpr int DOT_X = BOX_X + 1;
static constexpr int DOT_Y = BOX_Y + 1;
static constexpr int NUM_EDGE = BOX_X * BOX_Y * 4;
static constexpr int MAX_CHAINS = 9; 
static constexpr int DEADEND = -1;
static constexpr int REMOVED = -2;
static constexpr int NO_DOUBLE_DEAL = 101;
static constexpr int DOUBLE_DEAL = 102;
static constexpr int OPEN_CHAIN = 3;   
static constexpr int PRUNING = 20;
using namespace std;
using BoardLines = array<array<array<int8_t, 2>, 6>, 6>;   // input of run()
using XYZ = array<int8_t, 3>;
using pii = pair<int,int>;
using Clock = chrono::steady_clock;

extern XYZ eToXYZ[NUM_EDGE];
extern Clock::time_point c_startTime;
extern double g_timeLimitMs; // time limit of 24 seconds
extern double g_timeLeft;
extern double c_timeLimitMs;
extern bool g_timeUp;      
extern int prev_move_count; // To know if new game has started
extern long long g_nodes; 
extern array<int8_t, NUM_EDGE> order;

inline uint64_t encode_board_lines(const BoardLines &board) {
    uint64_t code = 0ULL;
    for (int x = 0; x < DOT_X; ++x) for (int y = 0; y < BOX_X; ++y) if (board[x][y][1]) code |= (1ULL << (y * 6 + x));
    for (int x = 0; x < BOX_X; ++x) for (int y = 0; y < DOT_Y; ++y) if (board[x][y][0]) code |= (1ULL << (30 + y * 5 + x));
    return code;
}

inline bool check_time() {
    auto elapsedMs = chrono::duration_cast<chrono::milliseconds>(Clock::now() - c_startTime).count();
    if (elapsedMs >= c_timeLimitMs) g_timeUp = true;
    return g_timeUp;
}

#endif 