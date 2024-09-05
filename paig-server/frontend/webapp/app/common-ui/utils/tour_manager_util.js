import {computed, observable} from 'mobx';

class TourManagerUtil {
    @observable tourSteps = []; 
    @observable tourState = false;
    @observable stepsChanged = false;
    @observable triggerTour = false;
    onExit = null;
    @observable tourStartStep = null;

    
    setTourData = (steps = [], onExit = null) => {
        if (onExit) {
            this.onExit = onExit;         
        }
        steps.sort((a,b)=> a.step - b.step);
        this.tourSteps = steps;
    }

    setTourOnExit = (onExit) => {
        this.onExit = onExit;
    }

    setTourStep = (step) => {
        const currentSteps = this.tourSteps;
        currentSteps.splice(step.step - 1, 0, step);
        this.tourSteps = currentSteps;
        this.stepsChanged = true;
    }

    exitTour = () => {
        this.tourState = false;
        if (this.onExit) {
            this.onExit();
        };
    }

    clearTourState = () => {
        this.tourState = false;
        this.tourSteps = [];
        this.onExit = null
    }

    startTour = (tourStartStep) => {
        this.tourStartStep = tourStartStep;
        this.tourState = true;
        this.triggerTour = true;
    }

    triggerTourAcknowledged = () => {
        this.triggerTour = false;
    }

    changeAcknowledged = () => {
        this.stepsChanged = false;
    }

    @computed
    get steps() {
        return this.tourSteps
    }

    @computed
    get tourStatus(){
        return this.tourState;
    }

    @computed
    get triggerTourStatus(){
        return this.triggerTour;
    }

    @computed
    get isStepChanged(){
        this.stepsChanged;
    }

    @computed
    get getTourStartStep(){
        return this.tourStartStep;
    }
}

const tourManagerUtil = new TourManagerUtil();
export default tourManagerUtil;