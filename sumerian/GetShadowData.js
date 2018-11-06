'use strict';

// Called when play mode starts.
//
function setup(args, ctx) {
	ctx.worldData.brake_status = 'OFF';
}

function enter(args, ctx) {
 	window.AWSIotData.getThingShadow({ thingName: 'WindTurbine1' }, (error, data) => {
 		if (error) {
 			console.error('Error getting state', error);

 			return ctx.transitions.failure();
 		}

 		const payload = JSON.parse(data.payload);

 		ctx.entityData.connected = payload.state.reported.connected;
		ctx.entityData.brake_status = payload.state.reported.brake_status;

		if (ctx.worldData.brake_status === 'OFF' && ctx.entityData.brake_status === 'ON') {
			ctx.worldData.brake_status = ctx.entityData.brake_status;
		} else if (ctx.entityData.brake_status === 'OFF') {
			ctx.worldData.brake_status = 'OFF';
		}

		//console.log(ctx.worldData.brake_status);
 		return ctx.transitions.success();
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
