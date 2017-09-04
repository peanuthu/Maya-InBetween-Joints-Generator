'''
The following script generates joints between two selected joints. Last edited by Mingjie on Sept. 3, 2017
'''
import maya.cmds as cmds

#---------------------------    
#  Create In Between Joints
#---------------------------  
def create_joints():
    
    # To check the any input from the window    
    joint_name=cmds.textField('name_textField',q=True,text=True)
    jntNum=cmds.intField('joint_num_intField',q=True,value=True)
    
    axisStatus=cmds.checkBox('local_axis',q=True,value=True)
    orientStatus=cmds.checkBox('clear_orient',q=True,value=True)
    
                
    # 1. To check whether a user has selected joints        
    if cmds.ls(sl=True,type='joint'):        
        # 1.1 Store the selected joints to variables
        sel=cmds.ls(sl=True,type='joint')
        # 1.2 To make sure only 2 joints are selected
        if len(sel)!=2:
            cmds.warning('Please select 2 joints.') 
        
        else:
            # 2. To determine which joint is the parent, and which is the child 
            if cmds.listRelatives(sel[0],p=True) and cmds.listRelatives(sel[0],p=True)[0]==sel[1]:
                parentJnt=sel[1]
                childJnt=sel[0]
    
            elif cmds.listRelatives(sel[1],p=True) and cmds.listRelatives(sel[1],p=True)[0]==sel[0]:
                parentJnt=sel[0]
                childJnt=sel[1]
                
            else:
                cmds.warning('The two joints selected are not in a parent-child hierarchy.')
                return
                
            # 3.1 To determine whether the input name and numbers are legit 
            # 3.1.1 To check if the input name has any number   
            for char in joint_name:
                if char.isdigit():
                    cmds.warning('The input should not contain any numbers. Please give another name.')
                    return 
            # 3.1.2 To check if the amount of in-between joints is reasonable   
            if jntNum<1:
                cmds.warning('Number of joints should not be less than 1.')
                return
            # 3.1.3 To check if the name of the in-between joints are same as the selected two joints
            if joint_name:
                if joint_name in parentJnt or joint_name in childJnt:
                    cmds.warning('The name may already exist in the scene. Please give another name.')
                    return
            
            # 3.2 Unparent the selected child and parent joints    
            cmds.parent(childJnt,w=True)
            # 3.3 To determine the location of the two selected joints in world space   
            parentJntpos=cmds.joint(parentJnt,q=True,p=True,a=True)
            childJntpos=cmds.joint(childJnt,q=True,p=True,a=True)
            # 3.4 To get the radius of the child joint
            childJntrad=cmds.joint(childJnt,q=True,rad=True)

            # 4. To build a curve(straight line) between the two joints based on the location info queryed in Step 3.3
            measureCurv=cmds.curve(d=1,p=[(parentJntpos[0],parentJntpos[1],parentJntpos[2]),(childJntpos[0],childJntpos[1],childJntpos[2])])
            # 4.1 To evenly place the cvs on the curve. The cvs will be furthered used for determining in-between joints location
            cmds.rebuildCurve(measureCurv,rpo=True,end=False,kep=True,s=jntNum+1,d=1)
                        
            # 5.1 If more than 1 in between joints need to be generated
            if jntNum>1:
                #5.1.1 Create a list to store the in-between joints and the parent joint               
                jointList=[]      
                jointList.append(parentJnt)
                # 5.1.2  Place the joints at the right location
                counter=1
                while jntNum-counter>=0:
                    cmds.select(cl=True)
                    # 5.1.3 proper names
                    if not joint_name:
                        newJnt=cmds.joint()
                    else:
                        newJnt=cmds.joint(n=joint_name+str(counter))
                    # 5.1.4 Place the joints at the right location    
                    cvPos=cmds.pointPosition(measureCurv+'.cv[%d]'%counter,w=True)
                    cmds.joint(newJnt,e=True,p=[cvPos[0],cvPos[1],cvPos[2]])
                    # 5.1.5 Display rotation axis if requested
                    if axisStatus==True:
                        cmds.setAttr(newJnt+'.dla',True)
                    # 5.1.6 Store the new joint in the list                            
                    jointList.append(newJnt)
                    # increment
                    counter=counter+1
                    
                # 5.1.6 Parent each in-between joints to the previous one and orient the joints   
                counter=1        
                while len(jointList)-counter>0:
                    cmds.parent(jointList[counter],jointList[counter-1])
                    cmds.joint(jointList[counter],e=True,o=[0,0,0],rad=childJntrad[0])          
                    counter=counter+1 
                # 5.1.7 parent the child joint to the last in-between joint                          
                cmds.parent(childJnt,jointList[counter-1])
                # 5.1.8 Orient the child joint if requested
                if orientStatus==True:
                    cmds.joint(childJnt,e=True,o=[0,0,0])
                    
            # 5.2 If only 1 in between joint needs to be generated   
            else:
                # 5.2.1 Create the joint with proper name
                if not joint_name:
                    newJnt=cmds.joint()
                else:
                    newJnt=cmds.joint(n=joint_name)
                # 5.2.2 Place the joint at the middle of the curve
                cvPos=cmds.pointPosition(measureCurv+'.cv[2]',w=True)
                cmds.joint(newJnt,e=True,p=[cvPos[0],cvPos[1],cvPos[2]])
                # 5.2.3 Display rotation axis if requested
                if axisStatus==True:
                    cmds.setAttr(newJnt+'.dla',True)                 
                # 5.2.4 Parent the joints properly with correct joint orient  
                cmds.parent(newJnt,parentJnt)
                cmds.joint(newJnt,e=True,o=[0,0,0],rad=childJntrad[0])
                cmds.parent(childJnt,newJnt)
                # 5.2.5 Orient the child joint if requested
                if orientStatus==True:
                    cmds.joint(childJnt,e=True,o=[0,0,0])
            # 6. Remove the curve
            cmds.delete(measureCurv)
    else:
        cmds.warning('Please select joints.')
    
#-------------------    
#    Create UI
#-------------------   
if cmds.window('InBetweenJointsGen',exists=True):
    cmds.deleteUI('InBetweenJointsGen')

cmds.window('InBetweenJointsGen')
cmds.window('InBetweenJointsGen',e=True,w=200,h=100)
cmds.showWindow('InBetweenJointsGen')

cmds.columnLayout('main_cl')
cmds.rowColumnLayout('text_rcl',nc=2)
cmds.text(label='Name:') 
cmds.textField('name_textField')
cmds.text(label='# of Joints')
cmds.intField('joint_num_intField',value = 1,minValue=1)


cmds.checkBox('local_axis',label='Display Local Rotation Axis')
cmds.checkBox('clear_orient',label='Zero Out Child Joint Orient')
cmds.button('create_button',label='Create Joints',command='create_joints()')  
cmds.button('cancel_button',label='Cancel',command='cmds.deleteUI("InBetweenJointsGen")')






            
                        