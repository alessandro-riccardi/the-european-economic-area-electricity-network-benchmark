def network_partitioning(atomic_agents, partitioning_strategy, Weighted_Adjacency_Matrix):

    number_atomic_agents = len(atomic_agents)

    if partitioning_strategy == "centralized":
        Control_Agents = [[]]
        for i in range(number_atomic_agents):
            Control_Agents[0].append(atomic_agents[i])
        Augmented_Control_Agents = Control_Agents.copy()

    elif partitioning_strategy == "distributed":
        Control_Agents = [[] for _ in range(number_atomic_agents)]
        for i in range(number_atomic_agents):
            Control_Agents[i].append(atomic_agents[i])

        number_control_agents = len(Control_Agents)
        Augmented_Control_Agents = [[] for _ in range(number_control_agents)]
        for l in range(0,number_control_agents):
            Augmented_Control_Agents[l] = Control_Agents[l].copy()
            Size_Control_Agent = len(Control_Agents[l])
            
            for i in range(0,number_atomic_agents):
                if atomic_agents[i] in Control_Agents[l]:
                    for j in range(0,number_atomic_agents):
                        if (Weighted_Adjacency_Matrix[i,j] != 0) and (atomic_agents[j] not in Control_Agents[l]):
                            Augmented_Control_Agents[l].append(atomic_agents[j])
            
            Augmented_Control_Agents[l] = list(set(Augmented_Control_Agents[l]))
            Augmented_Control_Agents[l].sort()
            print("Augmented control agent ", l, " : ", Augmented_Control_Agents[l])
        
    elif partitioning_strategy == "algorithmic":
        # Implement here the algorithmic partitioning strategy, which should be based on the network topology and the weighting matrices Q and R.
        pass
    elif partitioning_strategy == "genetic_algorithm":
        # Implement here the genetic algorithm partitioning strategy, which should be based on the network topology and the weighting matrices Q and R.
        pass
    elif partitioning_strategy == "load_partitioning":
        # Load a partition of the network from a file
        # Add argument to specify the file path in the argparser
        pass

    return Control_Agents, Augmented_Control_Agents