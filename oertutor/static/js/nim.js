NimGame = function(opt = {}){
    // Store reference to this instance
    _self = this;

    // HTML container in which game is displayed
    container = document.body;
    // Set up of Nim stacks
    stacks = new Array( 3, 4, 5);
    // Defines whose turn it is, -1 = AI, 1 = Human
    turn = 1;
    
    // History of actions
    playback = new Array();

    // Callback function that is executed on finish
    // Arguments:
    // winner - The winning player (-1 or 1), see NimGame.turn
    // playback - History of actions, see NimGame.playback
    cb_finished = function(winner, playback){
        alert('Game finished!\nPlayer '+winner+' won in '+playback.length);
    }

    // Initialization function
    init = function(opt){
        // Allow for overrides
        for( option in opt ){
            _self[option] = opt[option]
        }
        _self.play()
    }

    play = function(){
        // Check if game is not already finished, if so: exec callback and exit
        if(_self.is_finished()){
            _self.cb_finished(-1*_self.turn, _self.playback);
            return;
        }

        // If it is the human player's turn
        if(_self.turn == 1){
         
        // If it is the AI player's turn
        }else{

        }
    }

    // Returns true when the game is finished, false otherwise.
    // The game is finished when all stacks are set to 0
    is_finished = function(){
        for(var i = 0; i < _self.stacks.length; i++){
            if(_self.stacks[i] != 0) return false
        }
        return true
    }

    render = function(){
        stackstr = "";
        for(var i; i < _self.stacks.length; i++){
            stackstr += (stackstr==""?"":"|")+_self.stacks[i];
        }
        body = "|"+stackstr+"|";
        container.innerHTML = body;
    }

    apply = function(agent, stack, reduction){
        _self.playback[_self.playblack.length] = {
            "agent" : agent,
            "stacks" : _self.stacks,
            "stack": stack,
            "reduction": reduction
        }
        _self.stacks[stack] -= reduction
    }

    init(opt);
}
