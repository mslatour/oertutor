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

    end_turn = function(){
        _self.turn *= -1;
    }

    play = function(){
        // Check if game is not already finished, if so: exec callback and exit
        if(_self.is_finished()){
            _self.cb_finished(-1*_self.turn, _self.playback);
            return;
        }

        // Define the callback function for the input method
        input_cb = function(stack, reduction){
            _self.apply(_self.turn, stack, reduction)
            _self.end_turn();
        }
        // If it is the human player's turn
        if(_self.turn == 1){
            _self.get_human_input(_self.stacks,input_cb);
        // If it is the AI player's turn
        }else{
            _self.get_ai_input(_self.stacks,input_cb);
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

    // Gets input from the ai player for the next move
    get_ai_input = function(stacks, cb){
        return false;
    }

    // Gets input from the human player for the next move
    // The human player is requested to enter a valid stack number
    //   and a valid number to reduce the stack with.
    // If there is only one option the choice will be made automatically.
    get_human_input = function(stacks, cb){
        if( stacks.length > 1 ){
            stack = NaN;
            do{
                if( stacks.length > 2 ){
                    msg = "Choose a nonempty stack [1-"+stacks.length+"]"
                }else{
                    msg = "Choose a nonempty stack [1 or 2]"
                }
                stack = parseInt(prompt(msg))-1;
                if(
                    stack == NaN ||
                    stack < 0 ||
                    stack >= stacks.length ||
                    stacks[stack] == 0
                ){
                    alert("You have to enter the number of a nonempty stack");
                    stack = NaN;
                }
            }while(stack == NaN);
        }else{
            stack = 0;
        }
        if(stacks[stack] == 1){
            reduction = 1;
        }else{
            reduction = NaN;
            do{
                if(stacks[stack] == 2){
                    msg = "How much do you want to take from stack "+
                        stack+"? [1 or 2]";
                }else{
                    msg = "How much do you want to take from stack "+
                        stack+"? [1-"+stacks.length+"]";
                }
                reduction = parseInt(prompt(msg));
                if(
                    reduction == NaN || 
                    reduction < 1 || 
                    reduction > stacks[stack]
                ){
                    alert("You have to enter a valid number to reduce the stack");
                    reduction = NaN;
                }
            }while(reduction == NaN);
        }
        cb(stack, reduction);
    }
    init(opt);
}
