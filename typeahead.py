import sys

class Entry():
    
    def __init__(self, type, id, score, words, entry_num):
        self.type = type
        self.id = id
        self.score = score
        self.words = words
        self.entry_num = entry_num
    
    def __repr__(self):
        return self.id 

class PrefixNode():
    
    def __init__(self):
        self.edges = {}
        self.entries = set()

class PrefixTree(object):

    def __init__(self):
        self.root = PrefixNode()
    
    # Descend into the tree character by character,
    # adding the entry at each level, and create missing
    # nodes as needed
    def add(self, word, entry):
        node = self.root
        for char in word:
            try: 
                node = node.edges[char]
            except KeyError:
                node.edges[char] = PrefixNode()
                node = node.edges[char]
            node.entries.add(entry.id)
    
    # Descend into the tree character by character,
    # removing the entry at each level
    def remove(self, entry):
        for word in entry.words:
            node = self.root
            for char in word:
                node = node.edges[char]
                if entry.id in node.entries:
                    node.entries.remove(entry.id)
    
    # search is as simple as returning the list
    # of entries for the node at the end of the path
    # traced by the characters in prefix
    def search(self, prefix):
        node = self.root
        for char in prefix:
            try:
                node = node.edges[char]
            except KeyError:
                return set()
        return node.entries

valid_types = ["user", "topic", "question", "board"]

def add_fn(database, prefix_tree, command, command_num):

    command_comps = command.split()
    
    # verify the command length
    if (len(command_comps) < 4):
        raise ValueError("Invalid command - " + command)
    
    # verify the type
    type = command_comps[1]
    if type not in valid_types:
        raise ValueError("Invalid type in ADD command - " + command)
    
    # convert to lower case
    words = [word.lower() for word in command_comps[4:]]
    
    entry = Entry(command_comps[1], command_comps[2], float(command_comps[3]), words, command_num)
    
    # add the word to the prefix tree and the database
    for word in words:
        prefix_tree.add(word, entry)
    database[entry.id] = entry
    
def del_fn(database, prefix_tree, command):
    
    command_comps = command.split()
    
    # verify the command length
    if (len(command_comps) < 2):
        raise ValueError("Invalid command - " + command)
    
    entry_id = command_comps[1]
    
    if database.has_key(entry_id):
        prefix_tree.remove(database[entry_id])
        del database[entry_id]

# Common code path for QUERY and WQUERY commands
def perform_query(prefix_tree, search_strings, num_results, cmp_fn):
    
    # get the search results for each prefix
    sets = []
    for i in xrange(len(search_strings)):
        sets.append(prefix_tree.search(search_strings[i]))
    
    # take the intersection of the sets for each
    # search string then sort them by score and
    # only take the top num_results items
    if len(sets) > 0:
        result = list(set.intersection(*sets))
        result.sort(cmp=cmp_fn)
        result = result[:num_results]
        print " ".join(result)
    else:
        print ""
    
def query_fn(database, prefix_tree, command):

    command_comps = command.split()
    
    if (len(command_comps) < 3):
        raise ValueError("Invalid command - " + command)
    
    num_results = int(command_comps[1])
    if num_results < 1:
        print ""
        return
    
    search_strings = command_comps[2:]
    
    search_strings = [search_string.lower() for search_string in search_strings]
    
    # compare function which returns items in descending
    # order of score and with least recently added items
    # first when the scores are the same
    def cmp_fn(x, y):
        
        x = database[x]
        y = database[y]
        
        if x.score == y.score:
            return 1 if x.entry_num < y.entry_num else -1
        else:
            return 1 if x.score < y.score else -1
    
    perform_query(prefix_tree, search_strings, num_results, cmp_fn)
            
def wquery_fn(database, prefix_tree, command):
    
    command_comps = command.split()
    
    if (len(command_comps) < 4):
        raise ValueError("Invalid command - " + command)
    
    num_results = int(command_comps[1])
    if num_results < 1:
        print ""
        return
        
    num_boosts = int(command_comps[2])
    
    type_boosts = {type: 1.0 for type in valid_types}
    id_boosts = {}
    type_boosts_done = False
    
    for i in xrange(num_boosts):
        
        boost = command_comps[i+3].split(":")
        
        if boost[0] in valid_types and not type_boosts_done:
            type_boosts[boost[0]] *= float(boost[1])
        else:
            type_boosts_done = True
            if id_boosts.has_key(boost[0]):
                id_boosts[boost[0]] *= float(boost[1])
            else:
                id_boosts[boost[0]] = float(boost[1])
    
    search_strings = command_comps[num_boosts+3:]
    
    search_strings = [search_string.lower() for search_string in search_strings]
    
    # same function as in QUERY but apply
    # boosts to the scores first
    def cmp_fn(x, y):
        
        x = database[x]
        y = database[y]
        
        score_x = x.score * type_boosts[x.type]
        score_y = y.score * type_boosts[y.type]
        
        if id_boosts.has_key(x.id):
            score_x *= id_boosts[x.id]
        if id_boosts.has_key(y.id):
            score_y *= id_boosts[y.id]
        
        if score_x == score_y:
            return 1 if x.entry_num < y.entry_num else -1
        else:
            return 1 if score_x < score_y else -1
    
    perform_query(prefix_tree, search_strings, num_results, cmp_fn)
    
def main():
    
    # get the stdin
    input = sys.stdin.readlines()
    
    # make sure there is something to read
    if len(input) < 1:
        raise ValueError("Input was empty")
    
    N = int(input[0])
    
    # verify the length of the input
    if (len(input)) != N+1:
        raise ValueError("Number of lines in input did not match value of N")
    
    # create the database
    database = {}
    prefix_tree = PrefixTree()
    command_num = 0
    
    # create a dictionary of the command functions
    command_fns = {
        "ADD" : lambda cmd: add_fn(database, prefix_tree, cmd, command_num),
        "DEL" : lambda cmd: del_fn(database, prefix_tree, cmd),
        "QUERY" : lambda cmd: query_fn(database, prefix_tree, cmd),
        "WQUERY" : lambda cmd: wquery_fn(database, prefix_tree, cmd),
    }
    
    # execute each command
    for command in input[1:]:
        
        # strip newline character at the end of the string
        if command[-1] == '\n':
            command = command[:-1]
       
        # get the command name
        command_name = command.split()[0]
        
        # check that the command is valid
        if command_name not in command_fns.keys():
            raise ValueError("Unrecognized command - " + command_name)
        
        # run it
        command_fns[command_name](command)
        
        command_num += 1

if __name__ == "__main__":
    main()
