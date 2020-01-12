#Author-Autodesk Inc.
#Description-Create Fib

import adsk.core, adsk.fusion, traceback
import math

defaultPatternDiameter = 10
defaultSpiralPitch = 0.1
defaultInstances = 40

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface

newComp = None

def createNewComponent():
    # Get the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component

class FibCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            pattern = FibPattern()

            for input in inputs:
                if input.id == 'selection':
                    pattern.patternBodies = input.selection(0)
                elif input.id == 'pattern_diameter':
                    pattern.patternDiameter = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'spiral_pitch':
                    pattern.spiralPitch = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'secondary_spiral_pitch':
                    pattern.secondaryPitch = unitsMgr.evaluateExpression(input.expression, "cm")
                elif input.id == 'instances':
                    pattern.instances = unitsMgr.evaluateExpression(input.expression, "cm")
                    
            pattern.buildPattern()

            args.isValidResult = True

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FibCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FibCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()        
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = FibCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = FibCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            onDestroy = FibCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            handlers.append(onDestroy)

            #define the inputs
            inputs = cmd.commandInputs

            selectionInput = inputs.addSelectionInput('selection', 'Select', 'Basic select command input')
            selectionInput.setSelectionLimits(1,0)

            initPatternDiameter = adsk.core.ValueInput.createByReal(defaultPatternDiameter)
            inputs.addValueInput('pattern_diameter', 'Pattern Diameter','cm',initPatternDiameter)

            initSpiralPitch = adsk.core.ValueInput.createByReal(defaultSpiralPitch)
            inputs.addValueInput('spiral_pitch', 'Spiral Pitch','cm',initSpiralPitch)

            initSecondaryPitch = adsk.core.ValueInput.createByReal(0)
            inputs.addValueInput('secondary_spiral_pitch', 'Secondary Spiral Pitch','cm',initSecondaryPitch)

            initInstances = adsk.core.ValueInput.createByReal(defaultInstances)
            inputs.addValueInput('instances', 'Secondary Spiral Pitch','cm',initInstances)

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FibPattern:
    def __init__(self):
        self._patternDiameter = adsk.core.ValueInput.createByReal(defaultPatternDiameter)
        self._patternBodies = None
        self._spiralPitch = adsk.core.ValueInput.createByReal(defaultSpiralPitch)
        self._secondaryPitch = adsk.core.ValueInput.createByReal(0)
        self._intances = defaultInstances

    #properties
    @property
    def patternDiameter(self):
        return self._patternDiameter
    @patternDiameter.setter
    def patternDiameter(self, value):
        self._patternDiameter = value

    @property
    def patternBodies(self):
        return self._patternBodies
    @patternDiameter.setter
    def patternBodies(self, value):
        self._patternBodies = value

    @property
    def spiralPitch(self):
        return self._spiralPitch
    @spiralPitch.setter
    def spiralPitch(self, value):
        self._spiralPitch = value

    @property
    def secondaryPitch(self):
        return self._secondaryPitch
    @secondaryPitch.setter
    def secondaryPitch(self, value):
        self._secondaryPitch = value

    @property
    def instances(self):
        return self._intances
    @instances.setter
    def instances(self, value):
        self.i_nstances = value

    def buildPattern(self):
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        # Get the root component of the active design.
        rootComp = design.rootComponent
        features = rootComp.features
        
        # bodies = adsk.core.ObjectCollection.create()
        # bodies.add(input.selection(0).entity)


        # Create list of points
        curr_angle = 0
        curr_height = 0
        golden_angle = 2.4
        radius = 0
        for i in range(1,self._intances+1):
            curr_angle = i*golden_angle

            if self._secondaryPitch > 0:
                actual_height = i*self._spiralPitch * golden_angle / (2 * math.pi)
                # find angle of second spiral matching actual height
                intersectAngle = 2 * math.pi * actual_height / self._secondaryPitch


                secondary_angle = intersectAngle - (intersectAngle - curr_angle) % (2 * math.pi) + 2 * math.pi

                curr_height = secondary_angle * self._secondaryPitch / (2 * math.pi)

            else:
                curr_height = i*self._spiralPitch * golden_angle / (2 * math.pi)

            radius+=0.005
            # x = 0.5*self._patternDiameter*math.sin(curr_angle)
            # z = 0.5*self._patternDiameter*math.cos(curr_angle)
            x = 0
            z = 0

            # copyPasteBody = features.copyPasteBodies.add(bodies)
            copy = self._patternBodies.entity.copyToComponent(rootComp)
            
            bodies = adsk.core.ObjectCollection.create()
            bodies.add(copy)

            # Create a transform to do move

            # Create a move feature

            transform = adsk.core.Matrix3D.create()

            rotX = adsk.core.Matrix3D.create()
            rotX.setToRotation(curr_angle, adsk.core.Vector3D.create(0,1,0), adsk.core.Point3D.create(0,0,0))
            transform.transformBy(rotX)

            vector = adsk.core.Vector3D.create(x, curr_height, z)
            transform.translation = vector

            moveFeats = features.moveFeatures
            moveFeatureInput = moveFeats.createInput(bodies, transform)
            moveFeats.add(moveFeatureInput)



def run(context):
    try:
        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
            return
        commandDefinitions = ui.commandDefinitions
        #check the command exists or not
        cmdDef = commandDefinitions.itemById('Fib')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('Fib',
                    'Create Fib',
                    'Create a Fib.',
                    './resources') # relative resource file path is specified

        onCommandCreated = FibCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
