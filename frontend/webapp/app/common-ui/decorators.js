import 'babel-polyfill';

export function props(value) {
  return function decorator(target) {
    Object.assign(target.prototype, value);
  };
}

export function fsstore(props){
  return (target, property, descriptor) => {
    var fn = descriptor.value;
    descriptor.value = function () {
        if(!arguments.length) return fn.apply(this,new Array(props));
        let [last, ...first] = [...arguments].reverse();
        last = Object.assign(last, props);
          return fn.apply(this, [...([...first].reverse()), last]);
    };
  };
}