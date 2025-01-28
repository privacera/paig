import {isEmpty} from 'lodash';
import {observable} from 'mobx';
import {cloneDeep} from 'lodash';

import {GUARDRAIL_PROVIDER, GUARDRAIL_CONFIG_TYPE} from 'utils/globals';

class GuardrailFormUtil {
	@observable errors = {};
	steps = null;
	constructor(initialData = {}) {
		this.data = initialData;
	}
	setSteps(steps) {
	    this.steps = steps;
	}
	getSteps() {
	    return this.steps;
	}
	resetData(data={}) {
	    this.data = data;
	    this.lastData = cloneDeep(data);
	}

	// Set or update form data
	setData(newData) {
		this.data = {...this.data, ...newData};
	}

	// Get the current form data
	getData() {
		return this.data;
	}

	getSaveFormData () {
	    let data = cloneDeep(this.getData());

        if (!data.guardrailProvider) {
            delete data.guardrailProvider;
            delete data.guardrailConnectionName;
        }

        if (!data.description) {
            delete data.description;
        }

        data.guardrailConfigs = (data.guardrailConfigs || []).filter(c => c.status === 1);

        if (this.steps?.length) {
            let configTypes = this.steps.filter(s => s.configType).map(s => s.configType);

            data.guardrailConfigs = data.guardrailConfigs.filter(c => configTypes.includes(c.configType));
        }

        return data;
	}
	isDataChanged = () => {
	    if (!this.getData() || !this.lastData) {
            return false;
        }
	    return JSON.stringify(this.getData()) !== JSON.stringify(this.lastData);
	}

	// Set form errors
	setErrors(errors) {
		this.errors = errors;
	}

	// Get form errors
	getErrors() {
		return this.errors || {};
	}

	// Validate the entire form
	validate() {
		/*const errors = validators.validateAll(this.data);
		this.setErrors(errors);

		let keys = Object.keys(errors)
		let hasError = keys.some(key => {
            if (typeof errors[key] === 'object' && Object.keys(errors[key]).length) {
                return true;
            }
            if (typeof errors[key] === 'string') {
                return true;
            }
            return false;
        });

		return !hasError;*/

		return this.validateAll(this.data);
	}
	validateAll() {
	    let failedSteps = [];
        this.steps?.forEach(step => {
            let validationFunction = step?.validationFunction;
            let valid = this.validateFunction(validationFunction);
            if (!valid) {
                failedSteps.push(step.step);
            }
        });

        return {
            valid: !failedSteps.length,
            failedSteps
        }
	}
	validateField(fieldName, value, fieldKeyObject) {
	    let error = validators.validateField(fieldName, value);
	    if (!this.getErrors()[fieldKeyObject]) {
	        return;
	    }
        if (error) {
            this.getErrors()[fieldKeyObject][fieldName] = error;
        } else {
            delete this.getErrors()[fieldKeyObject][fieldName];
        }
	}
	getProvider() {
	    return this.data.guardrailProvider || GUARDRAIL_PROVIDER.PAIG.NAME;
	}

	getConfigForType(type) {
	    return this.data.guardrailConfigs?.find(config => config.configType === type);
	}
    validateFunction(functionName) {
        let newErrors = validators[functionName]?.(this.getData()) || {};
        const currentErrors = { ...this.getErrors() };

        const updatedErrors = { ...currentErrors, ...newErrors };
        this.setErrors(updatedErrors);

        let key = Object.keys(newErrors)[0];
        let errorObj = newErrors[key] || {};

        return Object.keys(errorObj).length === 0;
    }
}

const validators = {
    getConfigForType(data, type) {
        return data.guardrailConfigs?.find(config => config.configType === type);
    },
    validateField(fieldName, value) {
        let error = null;

        // Custom validation logic for each field
        switch (fieldName) {
            case "name":
                if (!value) error = "Name is required.";
                break;
            default:
                break;
        }

        return error;
    },
	validateBasicInfo(data) {
		const errors = {};
		if (!data.name) errors.name = 'Name is required.';

		if (data.guardrailProvider && !data.guardrailConnectionName) {
		    errors.guardrailConnections = 'Please select an account for enabled guardrail connections.';
		}

		return {basicInfo: errors};
	},
	validateContentModeration(data) {
	    const errors = {};

	    let config = this.getConfigForType(data, GUARDRAIL_CONFIG_TYPE.CONTENT_MODERATION.NAME);
	    if (config && config.status === 1) {
	        if (!config.configData?.configs?.length) {
                errors.contentModeration = 'Please add at least one content moderation filter.';
            }
	    }
	    return {contentModerationFilters: errors};
    },
    validateSensitiveDataFilters(data) {
        const errors = {};

        let config = this.getConfigForType(data, GUARDRAIL_CONFIG_TYPE.SENSITIVE_DATA.NAME);
        if (config && config.status === 1) {
            if (!data.guardrailProvider || data.guardrailProvider === GUARDRAIL_PROVIDER.PAIG.NAME) {
                if (!config.configData?.configs?.length) {
                    errors.sensitiveData = 'Please add at least one data filter to proceed.';
                }
            } else {
                let data = config.configData?.configs?.reduce((acc, curr) => {
                    if (curr.type === 'regex') {
                        acc.regex.push(curr);
                    } else {
                        acc.cat.push(curr);
                    }
                    return acc;
                }, {cat: [], regex: []});

                if (!data.cat.length && !data.regex.length) {
                    errors.sensitiveData = 'Please add at least one data filter to proceed.';
                }
            }
        }

        return {sensitiveDataFilters: errors};
    },
    validateOffTopicFilters(data) {
        const errors = {};

        let config = this.getConfigForType(data, GUARDRAIL_CONFIG_TYPE.OFF_TOPIC.NAME);
        if (config && config.status === 1) {
            if (!config.configData?.configs?.length) {
                errors.offTopic = 'Please add at least one off topic filter.';
            }
        }

        return {offTopicFilters: errors};
    },
    validateDeniedTerms(data) {
        const errors = {};

        let config = this.getConfigForType(data, GUARDRAIL_CONFIG_TYPE.DENIED_TERMS.NAME);
        if (config && config.status === 1) {
            let profanity = config.configData?.configs?.find(c => c.type === 'PROFANITY');
            if (profanity && (''+profanity.value) === 'false' && config.configData?.configs?.length === 1) {
                errors.deniedTerms = 'Please add at least one denied term, or enable profanity filter.';
            }
        }

        return {deniedTermsFilters: errors};
    },
    validatePromptSafety(data) {
        const errors = {};

        let config = this.getConfigForType(data, GUARDRAIL_CONFIG_TYPE.PROMPT_SAFETY.NAME);
        if (config && config.status === 1) {
            if (!config.configData?.configs?.length) {
                errors.promptSafety = 'Please select at least one prompt safety filter.';
            }
        }

        return {promptSafetyFilters: errors};
    },

	/*validateConfig(config) {
		const errors = {};
		if (!config.guardrailProvider) errors.guardrailProvider = 'Guardrail provider is required.';
		if (!config.configType) errors.configType = 'Config type is required.';
		if (typeof config.status !== 'number') errors.status = 'Status must be a number.';
		if (!config.responseMessage) errors.responseMessage = 'Response message is required.';

		if (config.configData?.configs?.length) {
			config.configData.configs.forEach((conf, index) => {
				const configErrors = {};
				if (!conf.category && !conf.type && !conf.topic && !conf.term) {
					configErrors.general = 'Config must have a category, type, topic, or term.';
				}
				if (conf.pattern && !conf.name) {
					configErrors.name = 'Name is required for regex patterns.';
				}
				if (conf.action && !['ALLOW', 'DENY', 'REDACT'].includes(conf.action)) {
					configErrors.action = 'Action must be ALLOW, DENY, or REDACT.';
				}
				if (Object.keys(configErrors).length) {
					errors[`configs[${index}]`] = configErrors;
				}
			});
		} else {
			errors.configData = 'Config data must contain configs.';
		}

		return errors;
	},

	validateGuardrailConfigs(guardrailConfigs) {
		const errors = [];
		guardrailConfigs.forEach((config, index) => {
			const configErrors = this.validateConfig(config);
			if (Object.keys(configErrors).length) {
				errors[index] = configErrors;
			}
		});
		return errors.length ? {
			guardrailConfigs: errors
		} : {};
	},*/

	validateAll(data) {
		/*return {
			...this.validateBasicInfo(data),
			...this.validateContentModeration(data),
			...this.validateSensitiveDataFilters(data),
			...this.validateOffTopicFilters(data),
			...this.validateDeniedTerms(data),
			...this.validatePromptSafety(data)
		};*/
	}
};

const initialData = {
	name: "",
	description: "",
	version: 1,
	guardrailProvider: '',
	guardrailConnectionName: '',
	guardrailConfigs: [],
	applicationKeys: []
};

export {
    GuardrailFormUtil,
    initialData
}