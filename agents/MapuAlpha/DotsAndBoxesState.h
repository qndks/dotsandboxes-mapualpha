// This implementation references ideas and structures from https://dotsandboxes.org/
// The algorithm was reimplemented and optimized for our competition environment.

#ifndef DOTSANDBOXESSTATE_H
#define DOTSANDBOXESSTATE_H

#include "common.h"
using namespace std;

struct DotsAndBoxesState
{
    int8_t opp[NUM_EDGE] = {                
        -1, 7, 20, -1, -1, 11, 24, 1, -1, 15, 28, 5, -1, 19, 32, 9, -1, -1, 36, 13,
        2, 27, 40, -1, 6, 31, 44, 21, 10, 35, 48, 25, 14, 39, 52, 29, 18, -1, 56, 33,
        22, 47, 60, -1, 26, 51, 64, 41, 30, 55, 68, 45, 34, 59, 72, 49, 38, -1, 76, 53,
        42, 67, 80, -1, 46, 71, 84, 61, 50, 75, 88, 65, 54, 79, 92, 69, 58, -1, 96, 73,
        62, 87, -1, -1, 66, 91, -1, 81, 70, 95, -1, 85, 74, 99, -1, 89, 78, -1, -1, 93
    };
    int8_t next[NUM_EDGE] = {             
        1, 2, 3, 0, 5, 6, 7, 4, 9, 10, 11, 8, 13, 14, 15, 12, 17, 18, 19, 16,
        21, 22, 23, 20, 25, 26, 27, 24, 29, 30, 31, 28, 33, 34, 35, 32, 37, 38, 39, 36,
        41, 42, 43, 40, 45, 46, 47, 44, 49, 50, 51, 48, 53, 54, 55, 52, 57, 58, 59, 56,
        61, 62, 63, 60, 65, 66, 67, 64, 69, 70, 71, 68, 73, 74, 75, 72, 77, 78, 79, 76,
        81, 82, 83, 80, 85, 86, 87, 84, 89, 90, 91, 88, 93, 94, 95, 92, 97, 98, 99, 96
    };
    int8_t prev[NUM_EDGE] = {
        3, 0, 1, 2, 7, 4, 5, 6, 11, 8, 9, 10, 15, 12, 13, 14, 19, 16, 17, 18,
        23, 20, 21, 22, 27, 24, 25, 26, 31, 28, 29, 30, 35, 32, 33, 34, 39, 36, 37, 38,
        43, 40, 41, 42, 47, 44, 45, 46, 51, 48, 49, 50, 55, 52, 53, 54, 59, 56, 57, 58,
        63, 60, 61, 62, 67, 64, 65, 66, 71, 68, 69, 70, 75, 72, 73, 74, 79, 76, 77, 78,
        83, 80, 81, 82, 87, 84, 85, 86, 91, 88, 89, 90, 95, 92, 93, 94, 99, 96, 97, 98
    };
    int8_t simplifiedBoxCount[NUM_EDGE] = {};           
    int8_t components[MAX_CHAINS] = {};        
    int8_t componentsCount = 0;        
    int8_t doubleDealState = 0;                
    int8_t score = 0;                    
    int8_t turn = 1;          
    int8_t remainingBoxes = BOX_X * BOX_Y;     

    DotsAndBoxesState() {}
    DotsAndBoxesState(const DotsAndBoxesState &o) : componentsCount(o.componentsCount), doubleDealState(o.doubleDealState), score(o.score), turn(o.turn), remainingBoxes(o.remainingBoxes) {
        memcpy(opp, o.opp, sizeof(opp));
        memcpy(next, o.next, sizeof(next));
        memcpy(prev, o.prev, sizeof(prev));
        memcpy(simplifiedBoxCount, o.simplifiedBoxCount, sizeof(simplifiedBoxCount));
        memcpy(components, o.components, sizeof(components));
    }
    void remove(int8_t e) {
        int8_t p = this->prev[e], n = this->next[e]; 
        this->next[p] = n;
        this->prev[n] = p;
        this->next[e] = REMOVED;
        this->prev[e] = REMOVED;
        this->opp[e] = REMOVED;
        this->simplifiedBoxCount[e] = REMOVED;
    }       
    void simplify(int8_t e) {
        int8_t ne = next[e];
        if (ne < 0 || ne == e || next[ne] != e) return;
        int8_t one = this->opp[ne], oe = this->opp[e];
        if (one == e) this->components[(this->componentsCount)++] = this->simplifiedBoxCount[oe] + 1;
        else {
            int8_t length = this->simplifiedBoxCount[ne] + this->simplifiedBoxCount[e] + 1;
            if (oe != DEADEND) {this->opp[oe] = one; this->simplifiedBoxCount[oe] = length;}
            if (one != DEADEND) {this->opp[one] = oe; this->simplifiedBoxCount[one] = length;}
            if (one == DEADEND && oe == DEADEND) this->components[(this->componentsCount)++] = -length; 
        }
        auto hide = [&](int8_t x){
            opp[x] = REMOVED;
            next[x] = REMOVED;
            prev[x] = REMOVED;
            simplifiedBoxCount[x] = REMOVED;
        };
        hide(e);
        hide(ne);
    }
    void removeAndSimplify(int8_t e) {
        if (e < 0) return;
        int8_t oe = this->opp[e], ne = this->next[e];
        this->remove(e);
        this->simplify(ne);
        if (oe < 0) return;
        int8_t noe = this->next[oe];
        this->remove(oe);
        this->simplify(noe);
    }
    void applyScore(int length, int leaveN, int minN) {
        this->turn  = -this->turn;
        this->score = -this->score;
        bool big = (length >= minN);
        int gain = big ? (length - leaveN) : length;
        this->score += gain;
        this->remainingBoxes -= gain;
        this->doubleDealState = big ? leaveN : 0;
    } 
    void getChildren(vector<DotsAndBoxesState> &children, vector<int8_t> *eList = nullptr) const;
};

#endif