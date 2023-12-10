"""
This is where the implementation of the plugin code goes.
The myPlugin-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('myPlugin')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class myPlugin(PluginBase):
  def main(self):
    active_node = self.active_node
    core = self.core
    self.namespace = None
    META = self.META
    # Log attributes of the active node
    logger = self.logger
    logger.debug('path: {0}'.format(self.core.get_path(active_node)))
    logger.info('name: {0}'.format(self.core.get_attribute(active_node, 'name')))
    logger.warn('pos : {0}'.format(self.core.get_registry(active_node, 'position')))
    logger.error('guid: {0}'.format(self.core.get_guid(active_node)))
    
    self.current_game_state = None
    self.game_state_name_counter = 0
    self.to_flip = []
    
    # Process nodes to create game states
    nodesList = self.core.load_sub_tree(active_node)
    # Dictionary to map node paths to node objects
    self.nodes = {}
    # Iterate through each node in the subtree
    for node in nodesList:
      # Map node path to node object
      self.nodes[self.core.get_path(node)] = node
    # List to hold all game state dictionaries
    all_states = []
    for path in self.nodes:
      node = self.nodes[path]
      # If the node is a GameState instance, process it
      if self.core.is_instance_of(node, self.META['GameState']):
        # Create and store the game state dictionary
        nodesList = self.nodes
        # Create a dictionary for the game state starting with the name
        path = self.core.get_path(node)
        game_state = {
          'name': self.core.get_attribute(node, 'name'),
          'path': path
        } 
        # Get the path to the current player and store it in the game state
        current_player_path = self.core.get_pointer_path(node, 'currentPlayer')
        # Load all children of the GameState node
        children = self.core.load_children(node)
        game_state['currentPlayer'] = self.core.get_attribute(
          nodesList[self.core.get_pointer_path(node, "currentPlayer")], 
          'name')
        game_state_node = self.core.get_pointer_path(self.active_node, "currentGameState")
        gs = nodesList[game_state_node]
        old_player = self.core.get_pointer_path(gs, "currentPlayer")
        self.logger.info("old_player: {}".format(old_player))
        old_player_node = self.core.load_by_path(self.root_node, old_player)
        old_player_color = self.core.get_attribute(old_player_node, "color")
        # Process and store the game board in the game state
        for child in children:
          if self.core.is_instance_of(child, self.META['Board']):
            # Initialize a list to represent the board
            board = [['' for _ in range(8)] for _ in range(8)]
            # Load all child nodes of the board, which should be tiles
            tiles = self.core.load_children(child)
            # Process each tile for flipping pieces
            for tile in tiles:
              if self.core.is_instance_of(tile, self.META["Tile"]):
                flips = []
                row = self.core.get_attribute(tile, "row")
                column = self.core.get_attribute(tile, "column")
                pieces = self.core.load_children(tile)
                # Initialize color as None in case there is no piece on the tile
                color = None
                if pieces:
                  piece = pieces[0]
                  if self.core.is_instance_of(piece, self.META['Piece']):
                    color = self.core.get_attribute(piece, 'color')
                  for board_child in tiles:
                    if self.core.is_instance_of(board_child, self.META["mightFlip"]):
                      srcTile = self.core.get_parent(self.nodes[self.core.get_pointer_path(board_child,"src")])
                      dstTile = self.core.get_parent(self.nodes[self.core.get_pointer_path(board_child,"dst")])
                      if srcTile == tile:
                        flips.append({
                          "column" : self.core.get_attribute(dstTile,"column"),
                          "row" : self.core.get_attribute(dstTile,"row")
                         }) 
                  board[column][row] = {"color": color, "flips": flips}
            self.board = board
            game_state['board'] = board
            all_states.append(game_state)
    
    # Codes from HW6 placed here: Check if the next move is viable  
    """
    current_node = self.active_node
    self.logger.info("current_node: {}".format(self.active_node))
    board = self.core.get_parent(current_node)
    self.logger.info("board: {}".format(board))
    gamestate = self.core.get_parent(board)
    self.logger.info("gamestate: {}".format(gamestate))
    current_board_path = self.core.get_path(gamestate)
    
    for i in range(0, len(all_states)):
      if (all_states[i].get('path') == str(current_board_path)):
        current_board = all_states[i]["board"]
        node = self.nodes[current_board_path]
        self.logger.info("node: {}".format(self.core.get_attribute(node, "name")))
        self.logger.info("node: {}".format(self.core.get_own_pointer_names(node)))
        # current piece
        current_move_pointer_path = self.core.get_pointer_path(node, "currentMove")
        self.logger.info("current_move_pointer_path: {}".format(current_move_pointer_path))
        piece = self.nodes[current_move_pointer_path]
        current_move_color= self.core.get_attribute(piece, "color")
        next_move_color = self.next_moves.get(current_move_color)
        # extract the current tile position     
        move_x = self.core.get_attribute(self.active_node, "row")
        move_y = self.core.get_attribute(self.active_node, "column")
        # First check if there is a piece on the current tile
        is_tile_occupied =  current_board[move_x][move_y]["color"]
        self.logger.info("is_tile_occupied: {}".format(is_tile_occupied))
        #check if the tile is empty or not
        if (is_tile_occupied == None):
          # Check if the next tile is of opposing color of the currentMove color
          for move in flip_directions:
            current_move_x = move_x +  move[0]
            current_move_y = move_y + move[1]
            # Check if we are at th ebounday of the board
            if (0 <= current_move_x < 8 )and(0 <= current_move_y < 8):
              # Get the color of the piece
              piece_color =  current_board[current_move_x][current_move_y]["color"]
              if (piece_color == current_move_color): 
                to_flips2.append((current_move_x, current_move_y))
                while((0 <= current_move_x < 7 )and (0 <= current_move_y < 7)):
                  current_move_x += move[0]
                  current_move_y += move[1]
                  piece_color = current_board[current_move_x][current_move_y]["color"]
                  to_flips2.append((current_move_x, current_move_y))
                  if (piece_color == next_move_color):
                    self.logger.info("Valid Move")
                    [self.to_flip.append(x) for x in to_flips2]
                    self.valid = True
                  to_flips2 = []                    
        else:
          self.logger.error("In valid move: Tile is occupied")
          self.valid = False
    self.logger.info("Can place next piece here: {}".format(self.valid))
    
    # Codes for HW7
    import re
    if not self.valid:
      self.logger.error("This is an invalid move")
      self.create_message(self.active_node, "This is an invalid move")
      return
    self.logger.info(self.to_flip)
    parent_state = self.core.get_parent(self.core.get_parent(self.active_node))
    self.logger.info(self.core.get_own_pointer_names(parent_state))
    current_move_path = self.core.get_pointer_path(parent_state, "currentMove")
    current_move_node = self.core.load_by_path(self.root_node, current_move_path)
    current_color = self.core.get_attribute(current_move_node, "color")
    self.next_move_color = "white" if current_color == "black" else "black"
    game_folder = self.core.get_parent(parent_state)
    self.row = self.core.get_attribute(self.active_node, "row")
    self.column = self.core.get_attribute(self.active_node, "column")
    parent_name = self.core.get_attribute(parent_state, "name")
    new_name = parent_name + "_1"
    try:
      for i, c in enumerate(parent_name):
        if c.isdigit():
          number_index = i
          break
      state_number = int(parent_name[number_index:]) + 1
      new_name = parent_name[:number_index] + f"{state_number}"
    except:
      pass
    copied_node = self.core.copy_node(parent_state, game_folder)
    self.core.set_attribute(copied_node, 'name', new_name)
    child_paths = self.core.get_children_paths(copied_node)
    old_player = self.core.get_pointer_path(copied_node, "currentPlayer")
    for child_path in child_paths:
      child = self.core.load_by_path(self.root_node, child_path)
      if self.core.is_instance_of(child, self.META["Player"]):
        if child_path != old_player:
          self.core.set_pointer(copied_node, "currentPlayer", child)
      if self.core.is_instance_of(child, self.META["Board"]):
        board = child
        tile_paths = self.core.get_children_paths(board)
        for tile_path in tile_paths:
          tile = self.core.load_by_path(self.root_node, tile_path)
          if self.core.get_attribute(tile, 'row') == self.row and self.core.get_attribute(tile, 'column') == self.column:
            self.logger.info("here")
            created_piece = self.core.create_node({'parent': tile, 'base': self.META["Piece"]})
            self.core.set_pointer(copied_node, "currentMove", created_piece)
            self.core.set_attribute(created_piece, "color", self.next_move_color)
          elif (self.core.get_attribute(tile, 'row'), self.core.get_attribute(tile, 'column')) in self.to_flip:
            if len(self.core.get_children_paths(tile)) > 0:
              piece_path = self.core.get_children_paths(tile)[0]
              self.core.set_attribute(self.core.load_by_path(self.root_node, piece_path), 'color', self.next_move_color)
    """
    self.util.save(self.root_node, self.commit_hash, self.branch_name)
    
  # Methods for the mini project
  def check_valid(self, tile):
    import math        
    active_node = tile      
    self.namespace = None         
    self.logger.info('Current Node : {0},{1}'.format(self.core.get_attribute(active_node,'row'), self.core.get_attribute(active_node,'column')))
    board = self.core.get_parent(active_node)
    gamestate = self.core.get_parent(board)
    nodesList = self.core.load_sub_tree(gamestate)                                          
    nodes = {}  
    for node in nodesList:      
      nodes[self.core.get_path(node)] = node  
      state = {}        
      state['name'] = self.core.get_attribute(gamestate, 'name')        
      self.logger.info(state)        
      current_player_path = self.core.get_pointer_path(gamestate, 'currentPlayer')        
      if current_player_path!=None :           
        state['currentPlayer'] = self.core.get_attribute(nodes[current_player_path],'name')        
      else :           
         state['currentPlayer']=None 
      row = self.core.get_attribute(active_node,'row')
      column = self.core.get_attribute(active_node,'column')
      state['currentMove'] = {'row':row,'column':column}        
      board = [[{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'}]
               , [{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'}]
               , [{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'}]
               ,[{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'}]
               , [{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'}]
               , [{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'}]
               , [{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'}]
               , [{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'},{'color':'none'}]
              ]        
      for child in self.core.get_children_paths(gamestate):          
        if (self.core.is_instance_of(nodes[child], META['Board'])):            
          for tile in self.core.get_children_paths(nodes[child]):              
            for piece in self.core.get_children_paths(nodes[tile]):
              board[self.core.get_attribute(nodes[tile],'row')][self.core.get_attribute(nodes[tile],'column')]['color'] = self.core.get_attribute(nodes[piece],'color')
      state['board'] = board
      self.logger.info(state['board'])
      self.logger.info("Gamestate node path before next{0}".format(gamestate["nodePath"]))
      next_game_state = self.core.copy_node(gamestate, self.core.get_parent(gamestate))
      self.core.set_pointer(next_gs,'prev',gamestate)
      next_name = self.core.get_attribute(gamestate,'name')+str(1)
      self.core.set_attribute(next_game_state,'name',next_name)
      next_nodes={}
      self.logger.info("Gamestate nodepath after next{0}".format(gamestate["nodePath"]))
      for node in self.core.load_sub_tree(next_gs) :      
        next_nodes[self.core.get_path(node)] = node 

  def count_color(self, color):
    color_count = 0
    children_pointer_list = self.core.get_children_paths(self.active_node)
    for children_pointer in children_pointer_list:
      child = self.nodes[children_pointer]
      if (self.core.is_instance_of(child, self.META['Board'])):
        for tile in self.core.get_children_paths(child):
          tile = self.nodes[tile]
          for piece_path in self.core.get_children_paths(tile):
            piece = self.nodes[piece_path]
            if color == self.core.get_attribute(piece, 'color'):
              color_count=color_count+1
    return color_count

  def flip_tiles(self, next_game_state, next_nodes, ft, player_color):
    next_board=None
    flipped_tiles = []
    for c in self.core.get_children_paths(next_game_state):
      child = next_nodes[c]
      if (self.core.is_instance_of(child,META['Board'])):
        next_board=child
        for tile in core.get_children_paths(next_board):
          tile=next_nodes[tile]
          next_pos=(core.get_attribute(tile,'row'), self.core.get_attribute(tile,'column'))
          for t in ft :
            if t==next_pos:
              flip_piece=next_nodes[self.core.get_children_paths(tile)[0]]
              core.set_attribute(flip_piece,'color',player_color)
              flipped_tiles.append(tile)
        return flipped_tiles 
                
  def undo(self):
    game_folder=self.core.get_parent(self.active_node)
    game_state=self.active_node
    nodesList = self.core.load_sub_tree(game_folder)                                          
    nodes = {}
    for node in nodesList:      
      nodes[self.core.get_path(node)] = node 
    prev_state_path=self.core.get_pointer_path(game_state,'prev')
    if prev_state_path is None : 
      self.logger.info("Can't undo initial game state ")
      return  
    prev_state=nodes[prev_state_path]#doubtfull
    self.core.set_pointer(game_folder,'currentState',prev_state)
    self.core.delete_node(game_state)
    self.util.save(self.root_node,self.commit_hash,self.branch_name)

  def check_tile_exist(self, tile, row_con, col_con):       
    return row_con < tile[0] or tile[1]> col_con or tile[0] < 0 or tile[1] < 0 
  
  def auto(self):
    valid_moves = self.highlight_valid_tiles()
    optimal_move = self.select_optimal_move(valid_moves)
    if optimal_move:
      self.place_piece(optimal_move)

  def select_optimal_move(self, valid_moves):
    return valid_moves[0] if valid_moves else None  

  def set_next_player(self, next_game_state, next_nodes):
    current_player_path = self.core.get_pointer_path(next_game_state,'currentPlayer')
    current_player = next_nodes[cp_path]
    for c in self.core.get_children_paths(next_game_state):
      child=next_nodes[c]
      if (self.core.is_instance_of(child, self.META['Player']) and child!=current_player):
        self.core.set_pointer(next_game_state,'currentPlayer',child)
        next_player_path=  self.core.get_pointer_path(next_game_state,'currentPlayer')
        next_player = next_nodes[np_path]                
        return core.get_attribute(next_player,'color')
         
  def set_next_move(self, next_game_state, next_nodes, pos, player_color):
    next_board = None
    for c in self.core.get_children_paths(next_game_state):
      child=next_nodes[c]
      if (self.core.is_instance_of(child,META['Board'])):
        next_board=child 
      for tile in self.core.get_children_paths(next_board):
        tile = next_nodes[tile]
        self.logger.debug(tile['nodePath'])
        self.logger.debug(next_gs['nodePath'])
        next_pos = (self.core.get_attribute(tile,'row'), self.core.get_attribute(tile,'column'))
        if next_pos == pos: 
          next_piece = self.core.create_child(tile,META['Piece'])
          next_nodes[self.core.get_path(next_piece)]=next_piece
          self.core.set_attribute(next_piece,'color',player_color)
          self.core.set_pointer(next_gs,'currentMove',next_piece)
          next_move_path=core.get_pointer_path(next_game_state,'currentMove')
          next_move = next_nodes[next_move_path]
          return self.core.get_attribute(next_move,'color')
      
  def check_valid_move(self, state):
    player = state['currentPlayer']
    currentMove = state['currentMove']
    if currentMove is None:
      return False
    currentColor = 'white' if player == 'PlayerBlack' else 'black'
    oppColor = 'black' if currentColor == 'white' else 'white'
    row, col = currentMove['row'], currentMove['column']
    result, tile_flip = process_directions(state, row, col, currentColor, oppColor)
    if result:
      self.logger.info('Is a valid move')
    else:
      self.logger.error('Not a Valid Move')
    return result, tile_flip

  def process_directions(self, state, row, col, currentColor, oppColor):
    tile_flip = []
    tile_flip_dir = [[] for _ in range(8)]
    valid = [False] * 8
    state = [-1] * 8
    result = False
    k = 0
    while any(state_val >= 0 for state_val in state):
      k += 1
      dirs = [(row, col + k), (row + k, col), (row, col - k), (row - k, col),
              (row + k, col + k), (row + k, col - k), (row - k, col + k), (row - k, col - k)]
      for i, direction in enumerate(dirs):
        state[i], temp_flip = is_tile_valid(state[i], direction, state['board'], currentColor, oppColor)
        tile_flip_dir[i].extend(temp_flip)
      result, valid = update_flip_tiles(state, valid, tile_flip_dir, tile_flip)
    if result:
      return result, tile_flip
    return result, tile_flip

  def is_tile_valid(self, state, direction, board, currentColor, oppColor):
    row, col = direction
    tile_flip = []
    if not check_tile_exist(row, col) or board[row][col]['color'] == "none":
      return float('-inf'), tile_flip
    if board[row][col]['color'] == oppColor:
      return 0, [(row, col)]
    if board[row][col]['color'] == currentColor and state == 0:
      return 1, []
    return state, tile_flip

  def update_flip_tiles(self, state, valid, tile_flip_dir, tile_flip):
    result = False
    for i in range(len(valid)):
      if state[i] > 0:
        valid[i] = True
        tile_flip.extend(tile_flip_dir[i])
      else:
        valid[i] = False
      result = result or valid[i]
    return result, valid