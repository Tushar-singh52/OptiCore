from typing import List, Dict

class ConflictGraph:
    def __init__(self, lectures: List):
        # 1. GRAPH: Adjacency list mapping lecture ID to list of conflicting lecture IDs
        self.adj_list: Dict[str, List[str]] = {lec.id: [] for lec in lectures}
        self.build_graph(lectures)

    def build_graph(self, lectures: List):
        n = len(lectures)
        for i in range(n):
            for j in range(i + 1, n):
                l1 = lectures[i]
                l2 = lectures[j]
                
                # GRAPH EDGES: Constraints
                # - Same teacher cannot be at two places at the same time
                # - Same section cannot have two classes simultaneously
                if l1.teacherId == l2.teacherId or l1.sectionId == l2.sectionId:
                    self.add_edge(l1.id, l2.id)

    def add_edge(self, u: str, v: str):
        if v not in self.adj_list[u]:
            self.adj_list[u].append(v)
        if u not in self.adj_list[v]:
            self.adj_list[v].append(u)

    def get_conflicts(self, lecture_id: str) -> List[str]:
        return self.adj_list.get(lecture_id, [])