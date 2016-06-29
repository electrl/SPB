import numpy as np
import copy as cp

class Ant():
    def __init__(self, graph, start_nodes, uid, ntv, ph_dep=10., alpha=1., beta=1., moves=1000):
        if alpha < 0 or beta < 1:
            raise Exception("alpha must by nonnegative and beta >= 1")
        
        self.__uid = uid
        
        self.__graph = graph
        
        # Global simulation properties
        
        self.__Alpha = alpha
        self.__Beta = beta
        self.__ph_dep = ph_dep # how much pheromone is begin deposited
        
        self.__start_nodes = start_nodes
        self.__start_node_idx = np.random.choice(self.__start_nodes)
        self.__g_nodes_to_visit = ntv
        
        # Iteration initial parameters
        
        self.__current_node = self.__graph.vertex(self.__start_node_idx)
        self.__nodes_to_visit = ntv
        
        # Parameters of solution
        self.__path = []
        self.__path.append(self.__start_node_idx)
        self.__pheromone_deposited = {}
        
        self.__path_cost = 0
        
        # Flag parameters to control agent state and solution
        self.__isActive = True
        self.__isMIA = False
        
        # Parameters to control agent exhaustion
        self.__max_moves = moves
        self.__moves = 0
        
    def get_cn(self):
        return self.__current_node
    
    def get_path(self):
        return self.__path
    
    def isActive(self):
        return self.__isActive
    
    def isMIA(self):
        return self.__isMIA
    
    def gen_prob(self, we_n, ph_n):
        z = we_n * ph_n
        return z / np.sum(z)
    
    def get_weights(self):
        # Get local info
        
        neigh_n = [ node for node in self.__current_node.out_neighbours() ]
        neigh_e = [ self.__graph.edge(self.__current_node, node) for node in neigh_n ]

        # Get properties values
        
        weights_n = np.array([ self.__graph.ep.weight[e] for e in neigh_e ]) ** (-1 * self.__Alpha)
        pheromone_n = np.array([ self.__graph.ep.pheromone_concentration[e] for e in neigh_e ]) ** self.__Beta
        
        prob_n = self.gen_prob(we_n=weights_n, ph_n=pheromone_n)
        
        return neigh_n, prob_n
    
    def move(self):
        neigh, prob_n = self.get_weights()
        node_n = np.random.choice(neigh, p=prob_n)
        node_n_idx = self.__graph.vertex_index[node_n]
        
        edge_n = self.__graph.edge(self.__current_node, node_n)
        
        # Update agent data
        
        self.__current_node = node_n
        self.__path.append( node_n_idx )
        self.__nodes_to_visit = [ node for node in self.__nodes_to_visit if node != node_n_idx ]
        self.__path_cost += self.__graph.ep.weight[edge_n]
        
        self.__moves += 1
        
        # Update individual pheromone trail
        
        self.__pheromone_deposited[ edge_n ] = self.__ph_dep
        
        # Check if solution is complete or whether stop condition is met
        
        if not self.__nodes_to_visit:
            self.__isActive = False
            
        elif self.__moves == self.__max_moves:
            self.__isActive = False
            self.__isMIA =  True
        
        return node_n
    
    def reset(self):
        # Get new starting point
        self.__start_node_idx = np.random.choice(self.__start_nodes)
        self.__current_node = self.__graph.vertex(self.__start_node_idx)
        
        # Reset iteration parameters
        self.__isActive = True
        self.__isMIA = False
        self.__moves = 0
        self.__nodes_to_visit = self.__g_nodes_to_visit
        self.__path = [self.__start_node_idx]
        self.__path_cost = 0
        self.__pheromone_deposited = {}

    
    def dump_trail(self):
        # Prepate pheromone trail
        ph_deposited = { e:  self.__pheromone_deposited[e] /self.__path_cost for e in self.__pheromone_deposited.keys() } 
        return ph_deposited
    
    def dump_path_cost(self):
        return self.__path_cost
 