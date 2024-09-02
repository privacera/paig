import FSBaseModel from 'common-ui/data/models/base_model';

class ResourceLookup extends FSBaseModel {
    userInput = "";
    resourceName = "";
    resources = {};
    appName="";
    startFrom="";

    constructor(props = {}, opts = {}) {
        super(props, opts);
        Object.assign(this, props);
    }

    toJSON = () => {
        return {
            userInput: this.userInput,
            resourceName: this.resourceName,
            resources: this.resources,
            appName: this.appName,
            appCode: this.appCode,
            startFrom:this.startFrom
        }
    }
}

export default ResourceLookup;