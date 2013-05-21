function NimGame(opt){
    // Store reference to this instance
    var _s = this;

    // HTML container in which game is displayed
    _s.container = document.body;
    // Set up of Nim stacks
    _s.stacks = new Array( 3, 4, 5);
    // Defines whose turn it is, -1 = AI, 1 = Human
    _s.turn = 1;
    
    // History of actions
    _s.playback = new Array();

    // Callback function that is executed on finish
    // Arguments:
    // winner - The winning player (-1 or 1), see NimGame.turn
    // playback - History of actions, see NimGame.playback
    _s.cb_finished = function(winner, playback){
        alert('Game finished!\nPlayer '+winner+' won in '+playback.length);
    }

    // Initialization function
    _s.init = function(opt){
        if(opt != undefined){
            // Allow for overrides
            for( option in opt ){
                _s[option] = opt[option]
            }
        }
        _s.play()
    }

    _s.end_turn = function(){
        _s.turn *= -1;
    }

    _s.play = function(){
        // Check if game is not already finished, if so: exec callback and exit
        if(_s.is_finished()){
            _s.cb_finished(-1*_s.turn, _s.playback);
            return;
        }

        // Render current state
        _s.render();

        // Define the callback function for the input method
        input_cb = function(stack, reduction){
            _s.apply(_s.turn, stack, reduction)
            _s.end_turn();
            _s.play()
        }
        // If it is the human player's turn
        if(_s.turn == 1){
            _s.get_human_input(_s.stacks,input_cb);
        // If it is the AI player's turn
        }else{
            _s.get_ai_input(_s.stacks,input_cb);
        }
    }

    // Returns true when the game is finished, false otherwise.
    // The game is finished when all stacks are set to 0
    _s.is_finished = function(){
        for(var i = 0; i < _s.stacks.length; i++){
            if(_s.stacks[i] != 0) return false
        }
        return true
    }   

    // Render the game state
    _s.render = function(){
        body = "| "+_s.stacks.join(" | ")+" |";
        _s.container.innerHTML = body;
    }

    // Apply the selected move
    _s.apply = function(agent, stack, reduction){
        _s.playback[_s.playback.length] = {
            "agent" : agent,
            "stacks" : _s.stacks,
            "stack": stack,
            "reduction": reduction
        }
        _s.stacks[stack] -= reduction
    }

    // Gets input from the ai player for the next move
    _s.get_ai_input = function(stacks, cb){
        cb(0,0);
    }

    // Gets input from the human player for the next move
    // The human player is requested to enter a valid stack number
    //   and a valid number to reduce the stack with.
    // If there is only one option the choice will be made automatically.
    _s.get_human_input = function(stacks, cb){
        if( stacks.length > 1 ){
            stack = NaN;
            do{
                if( stacks.length > 2 ){
                    msg = "Choose a nonempty stack [1-"+stacks.length+"]"
                }else{
                    msg = "Choose a nonempty stack [1 or 2]"
                }
                msg += "\nStacks content: | "+stacks.join(" | ")+" |";
                input = prompt(msg);
                if(input == null){
                    stop = confirm("Would you like to forfeit?");
                    if(stop){
                        return;
                    }else{
                        input = NaN;
                    }
                }
                stack = parseInt(input)-1;
                if(
                    isNaN(stack) ||
                    stack < 0 ||
                    stack >= stacks.length ||
                    stacks[stack] == 0
                ){
                    alert("You have to enter the number of a nonempty stack");
                    stack = NaN;
                }
            }while(isNaN(stack));
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
                        (stack+1)+"? [1 or 2]";
                }else{
                    msg = "How much do you want to take from stack "+
                        (stack+1)+"? [1-"+stacks[stack]+"]";
                }
                input = prompt(msg);
                if(input == null){
                    stop = confirm("Would you like to forfeit?");
                    if(stop){
                        return;
                    }else{
                        input = NaN;
                    }
                }
                reduction = parseInt(input);
                if(
                    isNaN(reduction) || 
                    reduction < 1 || 
                    reduction > stacks[stack]
                ){
                    alert("You have to enter a valid number to reduce the stack");
                    reduction = NaN;
                }
            }while(isNaN(reduction));
        }
        cb(stack, reduction);
    }

    //Initialize the game
    _s.init(opt);
}
