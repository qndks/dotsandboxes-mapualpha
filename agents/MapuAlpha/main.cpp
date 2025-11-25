// This implementation references ideas and structures from https://dotsandboxes.org/
// The algorithm was reimplemented and optimized for our competition environment.

#include "common.h" // macros
#include "TimeManager.h"
#include "DotsAndBoxesState.h"
namespace py = pybind11;
using namespace std;

TimeManager timeManager(g_timeLimitMs / 1000.0, BOX_X *DOT_Y + BOX_Y * DOT_X, BOX_X *BOX_Y);

int8_t minimax(const DotsAndBoxesState &gs, int depth, int alpha, int beta) {
    if (g_timeUp || (!(++g_nodes & 0x7FFF) && check_time())) return 0;
    if (!depth || !gs.remainingBoxes) return gs.doubleDealState ? int8_t(gs.score + (gs.remainingBoxes + (gs.remainingBoxes & 1)) / 2) : gs.score;
    static thread_local vector<DotsAndBoxesState> childBuf[64];
    vector<DotsAndBoxesState> &children = childBuf[depth];
    children.clear();
    gs.getChildren(children, nullptr);
    int val = -127;
    for (DotsAndBoxesState &child : children) {
        int v = (gs.turn == child.turn) ? minimax(child, depth - 1, alpha, beta) : -minimax(child, depth - 1, -beta, -alpha);
        val = max(val, v);
        if (val >= beta) return val;
        alpha = max(alpha, val);
    }
    return val;
}

XYZ choose_move(DotsAndBoxesState &gs) {
    DotsAndBoxesState original = gs; // Deep copy
    int8_t componentToEdge[MAX_CHAINS];
    int8_t discovered = 0;
    for (int8_t e = 0; e < NUM_EDGE; e++) {
        if (gs.opp[e] == REMOVED) continue;
        int8_t prev = gs.componentsCount;
        gs.simplify(e);
        if (gs.componentsCount != prev) componentToEdge[discovered++] = e;
    }
    int8_t doubleDealingEdge = DEADEND;
    int8_t loops[MAX_CHAINS];
    int8_t chains[MAX_CHAINS];
    int8_t loopsCount = 0;
    int8_t chainsCount = 0;
    for (int8_t e = 0; e < NUM_EDGE; e++) {
        int8_t oe = gs.opp[e];
        if (oe == REMOVED || gs.next[e] != e) continue;
        if (oe != DEADEND && gs.next[oe] == oe) {
            if (gs.simplifiedBoxCount[e] != 2) return eToXYZ[e];
            loops[loopsCount++] = e; 
        } else {
            if (gs.simplifiedBoxCount[e] != 1) return eToXYZ[e];
            chains[chainsCount++] = e; 
        }
        doubleDealingEdge = e; 
    }
    if (chainsCount && loopsCount) return eToXYZ[loops[0]];
    if (chainsCount > 1) return eToXYZ[chains[0]];
    if (loopsCount > 2) return eToXYZ[loops[0]];
    if (chainsCount == 1) gs.doubleDealState = 2;
    if (loopsCount == 2) gs.doubleDealState = 4;
    gs.removeAndSimplify(doubleDealingEdge);
    vector<int8_t> eList;
    vector<DotsAndBoxesState> children;
    gs.getChildren(children, &eList);
    size_t chSize = children.size();
    vector<pii> scores;
    scores.reserve(chSize);
    for (int i = 0; i < (int)chSize; i++) scores.emplace_back(i, 0);
    XYZ bestMove = {0, 0, 0};
    int depth = 2;
    while (depth++ < 60) {
        for (auto &[idx, val] : scores) {
            DotsAndBoxesState &child = children[idx];
            val = child.turn * minimax(child, depth - 1, -127, 127);
            if (g_timeUp) return bestMove;
        }
        sort(scores.begin(), scores.end(), [](const auto &A, const auto &B){ return A.second > B.second; }); // Move ordering
        int8_t e = eList[scores[0].first];
        if (e == NO_DOUBLE_DEAL) bestMove = eToXYZ[doubleDealingEdge];
        else if (e == DOUBLE_DEAL) bestMove = eToXYZ[original.next[original.opp[doubleDealingEdge]]];
        else if (e <= -OPEN_CHAIN) {
            int8_t componentNumber = - e - OPEN_CHAIN;
            int8_t componentEdge = componentToEdge[componentNumber];
            if (gs.components[componentNumber] == -2 && original.opp[componentEdge] == DEADEND) bestMove = eToXYZ[original.next[componentEdge]];
            else bestMove = eToXYZ[componentEdge];
        } else if (gs.simplifiedBoxCount[e] == 2) bestMove = eToXYZ[original.next[original.opp[e]]];
        else bestMove = eToXYZ[e];
    }
    return bestMove;
}

XYZ choose_move_wrapper(const BoardLines &board) {
    c_startTime = Clock::now();
    g_timeUp = false; // Is time over
    g_nodes = 0;      // How many nodes has been explored
    uint64_t code = encode_board_lines(board);
    int move_count = __builtin_popcountll(code);
    static thread_local mt19937 rng(random_device{}()); // Randomize order of node exploration
    if (prev_move_count > move_count) {
        g_timeLeft = g_timeLimitMs;                         // Reset timer
        shuffle(order.begin(), order.end(), rng);
    }
    prev_move_count = move_count;
    DotsAndBoxesState gs;
    static const int dx[4]={0,1,0,0}, dy[4]={0,0,1,0}, dir[4]={0,1,0,1};
    for (int8_t x=0; x<BOX_X; ++x){
        int8_t rowStart = 4*x;
        for (int8_t y=0; y<BOX_Y; ++y){
            int8_t up = rowStart + 20*y;
            int cnt=0;
            for(int k=0;k<4;k++) cnt += board[x+dx[k]][y+dy[k]][dir[k]] ? (gs.remove(up+k),1) : 0;
            if(cnt==4) gs.remainingBoxes--;
        }
    }
    c_timeLimitMs = timeManager.get_time_for_move(g_timeLeft / 1000.0, 60 - move_count, gs.remainingBoxes) * 1000;
    XYZ move = choose_move(gs);
    auto elapsedMs = chrono::duration_cast<chrono::milliseconds>(Clock::now() - c_startTime).count();
    g_timeLeft -= elapsedMs;
    return move;
}

PYBIND11_MODULE(MapuAlpha, m) {
    m.doc() = "The Final Model";
    m.def("choose_move", &choose_move_wrapper, py::arg("board_lines"), "Select move [x,y,z] for given board");
}
