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
    self.util.save(self.root_node, self.commit_hash, self.branch_name)
    
  # Methods for the mini project
  def highlight_valid_tiles(self):
    valid_tiles = []
    current_game_state_path = self.core.get_pointer_path(self.active_node,'currentGameState')
    game_state = self.nodes[current_game_state_path]
    self.logger.info("{0}".format(game_state))
    state_children_paths = self.core.get_children_paths(game_state)
    self.logger.info("{0}".format(state_children_paths))
    state_child_node = self.core.load_by_path(self.root_node, state_child_path)
    return valid_tiles

  def is_move_valid(self, row, col, board):
    return False  

  def count_pieces(self):
    game_state = self.active_node
    board = self.get_board(game_state)
    count = {'black': 0, 'white': 0}
    for row in board:
      for tile in row:
        if tile['color'] == 'black':
          count['black'] += 1
        elif tile['color'] == 'white':
          count['white'] += 1
    return count

  def perform_flipping(self):
    for row, col in self.to_flip:
      self.flip_piece(row, col)

  def flip_piece(self, row, col):
    game_state = self.active_node  
    board = self.get_board(game_state)
    tile = board[row][col]
    tile['color'] = 'white' if tile['color'] == 'black' else 'black'

  def undo(self):
    prev_state_path = self.core.get_pointer_path(self.active_node, 'prev')
    prev_state = self.core.load_by_path(self.root_node, prev_state_path)
    self.core.set_pointer(game_folder, 'currentState', prev_state)
    self.core.delete_node(self.active_node)
    self.util.save(self.root_node, self.commit_hash, self.branch_name)

  def auto(self):
    valid_moves = self.highlight_valid_tiles()
    optimal_move = self.select_optimal_move(valid_moves)
    if optimal_move:
      self.place_piece(optimal_move)

  def select_optimal_move(self, valid_moves):
    return valid_moves[0] if valid_moves else None  

  def place_piece(self, move):
    # Place a piece on the board as per the move
    if move:
      row, col = move
      board = self.current_game_state["board"]
      board[row][col]['color'] = 'black' 