import vrep
import quad_function
import numpy as np
import time
import math

quad_functions = None
try:
	vrep.simxFinish(-1)
	clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)

	if clientID != -1:
		vrep.simxSetIntegerSignal(clientID,'gripper_pos',0,vrep.simx_opmode_oneshot)
		quad_functions = quad_function.quad_helper(clientID)
		print('Simulazione iniziata: vedi in VREP')
		quad_functions.init_sensors()
		quad_functions.start_sim()
		#Setting initial time
		init_time = time.time()
		d1=0
		while vrep.simxGetConnectionId(clientID) != -1:
			elapsed_time = time.time()-init_time
			#Moving to grasping position
			if elapsed_time<20:
				#Setting model parameters and link lengths (da coordinate del simulatore)
				#NON SPOSTARE OGGETTI
				h = 0.1
				l1 = 0
				l2 = 0.18
				d_rt = 0.2
				y_off = 0.023
				#Getting object position and orientation respect to first joint
				obj_pos = quad_functions.get_obj_pos()
				obj_orien = quad_functions.get_obj_orien()
				#Inverse Kinematics
				joint_pos = quad_functions.get_joint_pos(obj_orien)
				joint_pos = [joint_pos[0],-joint_pos[1],joint_pos[2]]
				theta1 = joint_pos[1]
				theta2 = joint_pos[2]
				x = -l1- l2* math.cos(theta1) - d_rt
				y = -y_off
				z =  h-l2* math.sin(theta1)
				quad_pos = np.array(obj_pos) + np.array([x,y,z])
				if elapsed_time>10:
					if d1<d_rt:
						d1 = d1+0.001
					joint_pos[0] = d1
				quad_functions.set_joint_pos(joint_pos)
				quad_functions.move_quad(quad_pos)
			#Moving to safe position
			elif elapsed_time>40:
				quad_functions.move_quad([quad_pos[0]-0.2,quad_pos[1]+0.5,quad_pos[2]+0.2])
			#Opening gripper
			elif elapsed_time>35:
				vrep.simxSetIntegerSignal(clientID,'gripper_pos',0,vrep.simx_opmode_oneshot)
			#Moving to place position
			elif elapsed_time>30:
				quad_functions.move_quad([quad_pos[0],quad_pos[1]+1,quad_pos[2]])
			#Moving to safe position
			elif elapsed_time>=25:
				quad_functions.move_quad([quad_pos[0]-0.2,quad_pos[1]+0.5,quad_pos[2]+0.2])
			#Closing gripper
			elif elapsed_time>=20:
				vrep.simxSetIntegerSignal(clientID,'gripper_pos',1,vrep.simx_opmode_oneshot)

			vrep.simxSynchronousTrigger(clientID);

	else:
		print ("Failed to connect to remote API Server")
		quad_functions.stop_sim()
		vrep.simxFinish(clientID)
except KeyboardInterrupt:
	
	quad_functions.stop_sim()
	vrep.simxFinish(clientID)
