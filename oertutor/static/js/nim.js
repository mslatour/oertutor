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
        _s.init_render();
        _s.play();
    }

    _s.end_turn = function(){
        _s.turn *= -1;
    }

    _s.play = function(){
        // Check if game is not already finished, if so: exec callback and exit
        if(_s.is_finished()){
            _s.cb_finished(-1*_s.turn, _s.playback);
            _s.render();
            return;
        }

        // Define the callback function for the input method
        input_cb = function(stack, reduction){
            _s.apply(_s.turn, stack, reduction)
            _s.end_turn();
            _s.play()
        }
        // If it is the human player's turn
        if(_s.turn == 1){
            _s.get_human_input(input_cb);
        // If it is the AI player's turn
        }else{
            _s.get_ai_input(input_cb);
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

    // Initialize rendering
    _s.init_render = function(){
        // Creating div to put log message in
        var logger = document.createElement("div");
        logger.id = "nim-logger";
        // Append logger to the output container
        _s.container.appendChild(logger);
        
        // Create a container for the stacks
        var stackcontainer = document.createElement("div");
        stackcontainer.id = "nim-stack-container";
        stackcontainer.className = "nim stackcontainer";
        _s.container.appendChild(stackcontainer);
    }

    // Render the game state
    _s.render = function(clickcb){
        // Generating log message;
        log = "";
        for(var i = 0; i < _s.playback.length; i++){
            p = _s.playback[i];
            log += "| "+p.stacks.join(" | ")+" | <b>Agent "+p.agent+
                " reduced stack "+(p.stack+1)+" with "+p.reduction+"</b><br />" ;
        }
        // Add log message to logger
        document.getElementById("nim-logger").innerHTML = log;

        // Clear container for the stacks
        var stackcontainer = document.getElementById("nim-stack-container");
        stackcontainer.innerHTML = "";

        var stack, style;
        // Generate the stacks
        for(var i = 0; i < _s.stacks.length; i++){
            stack = document.createElement("div");
            if(_s.stacks[i] == 0){
                stack.className= "nim stack empty";
            }else{
                stack.className= "nim stack";
            }
            style = "height: "+(20+_s.stacks[i]*20)+"px;"+
                "left: "+(10+50*i)+"px;";
            stack.setAttribute("style", style);
            if(_s.stacks[i] > 0 && clickcb != undefined){
                // Create onclick action for stack.
                // It is necessary to create a new closure
                //   in which the current value of i will be kept.
                stack.addEventListener('click',function(stack){
                    return function(e){
                        clickcb(stack);
                    };
                }(i));
            }
            stack.innerHTML = _s.stacks[i];
            // Add stack to stack container
            stackcontainer.appendChild(stack);
        }
    }

    // Apply the selected move
    _s.apply = function(agent, stack, reduction){
        _s.playback.push({
            "agent" : agent,
            "stacks" : _s.stacks.slice(0), // .slice(0) clones array
            "stack": stack,
            "reduction": reduction
        });
        _s.stacks[stack] -= reduction
    }

    // Gets input from the ai player for the next move
    _s.get_ai_input = function(cb){
        // Declare placeholder for non-empty stacks
        var ne_stacks = new Array();

        var reduction, stack;

        // Calculate the nimsum of the stacks
        //   and store the indices of nonempty stacks
        var nimsum_stack = 0;
        for(var i = 0; i < _s.stacks.length; i++){
            if(_s.stacks[i] > 0){
                ne_stacks.push(i);
                nimsum_stack ^= _s.stacks[i];
            }
        }
        // General case, use the nimsum operator to determine
        //   which stack should be picked by observing which
        //   stack decreases in size when nimsum-ed with the 
        //   nimsum of all the stacks.
        for(var i = 0; i < ne_stacks.length; i++){
            stack = ne_stacks[i];
            // If the nimsum operator 
            if((_s.stacks[stack]^nimsum_stack) < _s.stacks[stack]){
                reduction = _s.stacks[stack] - (_s.stacks[stack]^nimsum_stack);
                cb(stack, reduction);
                return;
            }

        }
        // No stack was reduced by the nimsum operator
        //   which means the stacks are equally sized.
        // In that case pick a random stack and either take everything
        //   or everything but one. The latter is the case when there 
        //   are an even number of equally sized stacks.
        var index = Math.floor(Math.random()*ne_stacks.length)
        stack = ne_stacks[index];
        if(ne_stacks.length % 2 == 0){
            reduction = ( _s.stacks[stack] > 1 ? _s.stacks[stack]-1 : 1 );
        }else{
            reduction = _s.stacks[stack];
        }
        cb(stack, reduction);
        return;
    }

    // Gets input from the human player for the next move
    // The human player is requested to enter a valid stack number
    //   and a valid number to reduce the stack with.
    // If there is only one option the choice will be made automatically.
    _s.get_human_input = function(cb){
        clickcb = function(stack){
            var reduction;
            if(_s.stacks[stack] == 1){
                reduction = 1;
            }else{
                reduction = NaN;
                do{
                    if(_s.stacks[stack] == 2){
                        msg = "How much do you want to take from stack "+
                            (stack+1)+"? [1 or 2]";
                    }else{
                        msg = "How much do you want to take from stack "+
                            (stack+1)+"? [1-"+_s.stacks[stack]+"]";
                    }
                    input = prompt(msg);

                    if(input == null) return false;

                    reduction = parseInt(input);
                    if(
                        isNaN(reduction) || 
                        reduction < 1 || 
                        reduction > _s.stacks[stack]
                    ){
                        alert("You have to enter a valid number to reduce the stack");
                        reduction = NaN;
                    }
                }while(isNaN(reduction));
            }
            cb(stack, reduction);
            return true;
        };
        _s.render(clickcb);
    }

    //Initialize the game
    _s.init(opt);
}
