class ConfigProperties {
	properties = []
	propertiesName = {
        SHIELD_CONFIGURATION: 'SHIELD_CONFIGURATION',
        VECTOR_DB: 'VECTOR_DB'
	}
	setProperties = (properties) => {
        this.properties = properties;
    }

    isShieldConfigEnable() {
        return this.checkIsEnable(this.propertiesName.SHIELD_CONFIGURATION, false);
    }

    isVectorDBEnable() {
        return this.checkIsEnable(this.propertiesName.VECTOR_DB, false);
    }

    checkIsEnable(propertyName, upperCase = false) {
        if (Array.isArray(this.properties.slice())) {
            let property = this.properties.find(property => {
                let propName = upperCase ? property.name.toUpperCase() : property.name;
                return propName == propertyName;
            });
            if (property && property.value) {
                let value = property.value.toLowerCase();
                return (value == "enable" || value == "enabled" || value == "true");
            }
        }
        return false;
    }
    getPropertyValue(propertyName) {
        if (this.properties) {
            let found = this.properties.find(property => property.name == propertyName);
            return found && found.value || "";
        }
        return "";
    }
}

const configProperties = new ConfigProperties();
export {
    configProperties
}