// This implementation references ideas and structures from https://dotsandboxes.org/
// The algorithm was reimplemented and optimized for our competition environment.

#include "DotsAndBoxesState.h"
using namespace std;

inline void pushChild(vector<DotsAndBoxesState> &children, vector<int8_t> *eList, DotsAndBoxesState &&st, int8_t tag){
    children.emplace_back(move(st));
    if (eList) eList->push_back(tag);
}

void DotsAndBoxesState::getChildren(vector<DotsAndBoxesState> &children, vector<int8_t> *eList) const {
    int reserveCount = (this->doubleDealState ? 2 : PRUNING + 2);
    children.clear(); children.reserve(reserveCount);
    if (eList) {eList->clear(); eList->reserve(reserveCount);}
    if (this->doubleDealState) {
        auto addChild = [&](int8_t tag, bool giveToOpponent) {
            DotsAndBoxesState ns = *this;
            if (giveToOpponent) {ns.score *= -1; ns.turn *= -1;}
            ns.score += ns.doubleDealState;
            ns.remainingBoxes -= ns.doubleDealState;
            ns.doubleDealState = 0;
            pushChild(children, eList, move(ns), tag);
        };
        addChild(NO_DOUBLE_DEAL, false); 
        addChild(DOUBLE_DEAL, true);  
        return;
    }
    for (size_t k = 0; k < order.size(); ++k) {
        int8_t e = order[k], oe = this->opp[e];
        if (e < oe || oe == REMOVED) continue;
        int8_t ne = this->next[e], nne = this->next[ne], nnne = this->next[nne];
        int8_t e3 = ((ne==oe || nne==oe || nnne==oe) && (ne==e || nne==e || nnne==e)) ? (ne==e ? nne : ne) : REMOVED;
        int8_t length = this->simplifiedBoxCount[e] + (e3 == REMOVED ? 0 : this->simplifiedBoxCount[e3] + 1);
        DotsAndBoxesState ns = *this;
        ns.removeAndSimplify(e);
        ns.removeAndSimplify(e3);
        ns.applyScore(length, 2, 3);
        pushChild(children, eList, move(ns), e);
        if (children.size() >= PRUNING) break;
    }
    int8_t bestChainSize = 26, bestLoopSize = 26, bestChain = -1, bestLoop = -1;
    for (int i = 0; i < componentsCount; i++) {
        int8_t cs = this->components[i];
        if (cs<0 && -cs < bestChainSize) {bestChainSize = -cs; bestChain = i;} 
        else if (cs < bestLoopSize) {bestLoopSize = cs; bestLoop = i;}
    }
    auto openComp = [&](int idx){
        DotsAndBoxesState ns = *this;
        int8_t raw = components[idx];
        bool isChain = (raw < 0);
        int length = abs(raw), leaveN = (isChain ? 2 : 4), minN = (isChain ? 3 : 4);
        ns.applyScore(length, leaveN, minN);
        ns.components[idx] = ns.components[--ns.componentsCount];
        pushChild(children, eList, move(ns), int8_t(-OPEN_CHAIN - idx));
    };
    if (bestChain >= 0) openComp(bestChain);
    if (bestLoop >= 0) openComp(bestLoop);
    return;
}
