'use strict';

// Called when play mode starts.
//
function setup(args, ctx) {
}

function update(args, ctx) {
}

function enter(args, ctx) {
	var msg = '{"deviceId":"202481602013867"}';
	var aa = btoa(msg);
	var params = {
	  FunctionName: 'WindfarmGetTurbineLiveStats',
	  InvocationType: 'RequestResponse',
	  LogType: 'None',
	  Payload: msg
	};
	var lambda = new window.AWS.Lambda({region: 'us-west-2'});
	lambda.invoke(params, function(err, data) {
	  if (err) {
		console.log(err, err.stack); // an error occurred
		//console.error('Error getting state', error);
		return ctx.transitions.failure();
	  }
	  else {
		const payload = JSON.parse(data.Payload);
		console.log(payload);
		if (payload.turbine_speed != "unknown") {
		    ctx.entityData.turbine_speed = payload.turbine_speed;
			ctx.entityData.turbine_voltage = payload.turbine_voltage;
			ctx.entityData.turbine_temp = payload.turbine_temp;
			ctx.entityData.turbine_vibe_x = payload.turbine_vibe_x;
			ctx.entityData.turbine_vibe_y = payload.turbine_vibe_y;
			ctx.entityData.turbine_vibe_z = payload.turbine_vibe_z;
			document.getElementById('vSpeed').innerHTML = ctx.entityData.turbine_speed;
			document.getElementById('vVoltage').innerHTML = ctx.entityData.turbine_voltage;
			document.getElementById('vTemp').innerHTML = ctx.entityData.turbine_temp;
			document.getElementById('vVibeX').innerHTML = ctx.entityData.turbine_vibe_x;
			document.getElementById('vVibeY').innerHTML = ctx.entityData.turbine_vibe_y;
			document.getElementById('vVibeZ').innerHTML = ctx.entityData.turbine_vibe_z;
		    return ctx.transitions.success();
		}
		else {
			return ctx.transitions.failure();
		}
		//console.log(data);           // successful response
	  }
  });
}

// When used in a ScriptAction, called when a state is exited.
//
function exit(args, ctx) {
}

// Called when play mode stops.
//
function cleanup(args, ctx) {
}

// Defines script parameters.
//
var parameters = [];
