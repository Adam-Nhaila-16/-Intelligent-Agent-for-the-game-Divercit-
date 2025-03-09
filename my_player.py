from player_divercite import PlayerDivercite
from seahorse.game.action import Action
from seahorse.game.game_state import GameState
from game_state_divercite import GameStateDivercite
from seahorse.utils.custom_exceptions import MethodNotImplementedError

#from seahorse import Piece

from seahorse.game.game_layout.board import Piece


import time  # Import the time module to track elapsed time



class MyPlayer(PlayerDivercite):
    """
    Player class for Divercite game that makes random moves.

    Attributes:
        piece_type (str): piece type of the player
    """

    def __init__(self, piece_type: str, name: str = "MyPlayer"):
        """
        Initialize the PlayerDivercite instance.

        Args:
            piece_type (str): Type of the player's game piece
            name (str, optional): Name of the player (default is "bob") 
            time_limit (float, optional): the time limit in (s)
        """
        super().__init__(piece_type, name)

    def compute_action(self, current_state: GameState, remaining_time: int = 1e9, **kwargs) -> Action:
        """
        Use the minimax algorithm to choose the best action based on the heuristic evaluation of game states.

        Args:
            current_state (GameState): The current game state.

        Returns:
            Action: The best action as determined by minimax.
        """

        #On regarde l'étape du jeu auquel on se trouve (correspond au nombre de coups joués par notre agent)
        global count_step
        self.count_step+=1
        #Remarque : count_step est initialisé plus bas dans le code car impossibilité 
        # d'initialiser au dessus de la fonction compute_action à cause des exigeances pour le code.

        #Gestion dynamique de la profondeur de recherche en fonction de l'étape du jeu
        if self.count_step<=10:
            best_action = self.minimax(current_state, 2)
            print("self.count_step vaut et 2", self.count_step)
        elif self.count_step>10 and self.count_step<=14:
            best_action = self.minimax(current_state, 3)
            print("self.count_step vaut et 3", self.count_step)
        else:
            best_action = self.minimax(current_state,4)
            print("self.count_step vaut et 4", self.count_step)
        
        
    
        # On regarde si aucune action valide n'a été trouvée (à priori cela n'arrive jamais)
        if best_action is None:
            raise MethodNotImplementedError("No valid actions found.")
    
        return best_action
    
    count_step=0


    def maxValue(self, state: GameState, depth: int, alpha: float, beta: float):
        """
        Fonction de maximisation pour Minimax avec élagage alpha-bêta.

        Args :
            state (GameState) : L'état actuel du jeu
            depth (int) : Profondeur de recherche
            alpha (float) : Valeur alpha pour l'élagage
            beta (float) : Valeur beta pour l'élagage

        Returns :
            (Action, int) : Meilleure action et sa valeur
        """

        #On génère les actions possible à partir de notre état
        possible_actions = state.generate_possible_heavy_actions()
        
        #Si le jeu est fini ou si la profondeur de recherche arrive à 0 : On renvoie l'estimation de l'heuristique
        if state.is_done() or depth == 0:
            return None, self.heuristic_evaluation(state)


        #Recherche de l'action qui maximise l'heuristique (avec gestion de la profondeur dynamique)
        best_action = None
        max_value = float('-inf')

        for action in possible_actions:
            new_state = action.get_next_game_state()
            _, new_value = self.minValue(new_state, depth - 1, alpha, beta)

            if new_value > max_value:
                max_value = new_value
                best_action = action
            
            # Alpha-Beta Pruning
            if max_value >= beta:
                break  # Cut-off
            alpha = max(alpha, max_value)

        return best_action, max_value

    def minValue(self, state: GameState, depth: int, alpha: float, beta: float):
        """
        Fonction de minimisation pour Minimax avec élagage alpha-bêta.

        Args :
            state (GameState) : L'état actuel du jeu
            depth (int) : Profondeur de recherche
            alpha (float) : Valeur alpha pour l'élagage
            beta (float) : Valeur beta pour l'élagage

        Returns :
            (Action, int) : Meilleure action et sa valeur
        """

        #On génère les actions possible à partir de notre état
        possible_actions = state.generate_possible_heavy_actions()

        #Si le jeu est fini ou si la profondeur de recherche arrive à 0 : On renvoie l'estimation de l'heuristique
        if state.is_done() or depth == 0:
            return None, self.heuristic_evaluation(state)


        #Recherche de l'action qui maximise l'heuristique (avec gestion de la profondeur dynamique)
        best_action = None
        min_value = float('inf')

        for action in possible_actions:
            new_state = action.get_next_game_state()
            _, new_value = self.maxValue(new_state, depth - 1, alpha, beta)

            if new_value < min_value:
                min_value = new_value
                best_action = action
            
            # Alpha-Beta Pruning
            if min_value <= alpha:
                break  # Cut-off
            beta = min(beta, min_value)

        return best_action, min_value

    def minimax(self, state: GameState, depth: int):
        """
        Fonction principale pour l'algorithme Minimax avec élagage alpha-bêta.

        Args :
            state (GameState) : L'état actuel du jeu
            depth (int) : Profondeur de recherche

        Returns :
            Action : La meilleure action trouvée
        """
        
        action, _ = self.maxValue(state, depth, float('-inf'), float('inf'))
        return action


    
    def heuristic_evaluation(self, state: GameState) -> int:
        """
        Évalue l'état du jeu pour guider la recherche Minimax.

        Args :
            state (GameState) : L'état actuel du jeu

        Returns :
            int : Score heuristique de l'état
        """
       
        
        possible_actions = list(state.generate_possible_heavy_actions())
        my_id =  self.get_id()


        if state.players[1].get_id() == my_id :
            opponent_id = state.players[0].get_id()
        else:
            opponent_id = state.players[1].get_id()

        
        resources_left = self.get_ressources_left(my_id, state)
        
        # Choix d’initialisation du score : Score de mon agent – Score de l’adversaire
        score = state.scores[my_id] - state.scores[opponent_id] 

        # On revoie simplement le score si aucune action n'est possible
        if not possible_actions:
            return score  
        
        
        
        #Penser à Valoriser la différence des 2 scores si posssible

        
        # Récompenser notre agent lorsqu’il pose ses cités
        for piece, n_piece in state.players_pieces_left[my_id].items():
            if piece[1] == "C":  # Vérifie si c'est une cité
                score += 2 * (8- n_piece)  # Ajouter au score 8 * (2-n_piece) points pour chaque cité posée
        #Le choix de récompense pour le dépôt de cités est purement empirique ici
        

        if 3 in resources_left.values() and 0 in resources_left.values():
            
            score-=2
        

        

        for pos in state.get_rep().get_env().keys():
            if state.check_divercite(pos):
                #Récompenser les états où nous avons des divercités
                if self.is_player_piece(pos, my_id,state):
                
                    score += 5  
            
                #Pénaliser si l'adversaire a une divercité
                if self.is_player_piece(pos, opponent_id,state):
                
                    score -= 2 

            
      
             
        
        # Pénaliser si plusieurs ressources de la même couleur autour d’une cité de cette même couleur
        # (Pendant la moitié de la partie environ)
        if self.count_step<=11 and self.countnstack(my_id, 2,state)!=0 :
            
            score-= self.countnstack(my_id, 2,state) # -1 pour chaque stack de 2 ressources de la même couleur
            
        
        if self.count_step<=12 and self.countnstack(my_id, 3,state)!=0 :
            
            score-= self.countnstack(my_id, 3,state) # -1 pour chaque stack de 3 ressources de la même couleur
        

        
            
        return score
        
    def is_player_piece(self, pos: tuple[int, int], player_id: int,state: GameState) -> bool:
        """
        Vérifie si la pièce à une position appartient au joueur.

        Args :
            pos (tuple) : Position sur le plateau
            player_id (int) : ID du joueur

        Returns :
            bool : Vrai si la pièce appartient au joueur
        """
        piece = state.get_rep().get_env().get(pos)
        return piece is not None and piece.get_owner_id() == player_id
    
    
    def countnstack(self,player_id, n, state: GameState ) -> int:
        """
        Compte le nombre de positions avec exactement n ressources identiques autour d'une cité.

        Args :
            player_id (int) : ID du joueur
            n (int) : Nombre de ressources identiques
            state (GameState) : L'état actuel du jeu

        Returns :
            int : Nombre de positions correspondant
        """
        board = state.get_rep()
        d = board.get_dimensions()
        env = board.get_env()
        return sum([sum([p[0].get_type()[0] == env[(i,j)].get_type()[0] for p in board.get_neighbours(i,j).values() if isinstance(p[0], Piece)]) == n for i in range(d[0]) for j in range(d[1]) if state.in_board((i,j)) and env.get((i,j)) and env.get((i,j)).get_type()[1] == 'C' and env[(i,j)].get_owner_id() == player_id])
    

    def get_ressources_left(self, player_id: int, state: GameState) -> dict:
        """
        Retourne le nombre de ressources restantes pour chaque type pour un joueur.

        Args :
            player_id (int) : ID du joueur
            state (GameState) : L'état actuel du jeu

        Returns :
            dict : Dictionnaire des ressources restantes
        """
        pieces = state.players_pieces_left[player_id]
        resources_left = {}

        for resource, count in pieces.items():
            if resource[1] == 'R':  # Vérifie que c'est bien une ressource (et non pas une cité)
                resources_left[resource] = count

        return resources_left
