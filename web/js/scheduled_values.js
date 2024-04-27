import { app } from "../../../scripts/app.js";
function loadChartJs(callback) {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = () => {
        const pluginScript = document.createElement('script');
        pluginScript.src = 'https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@1.0.1/dist/chartjs-plugin-zoom.min.js';
        pluginScript.onload = callback;
        document.head.appendChild(pluginScript);
    };
    document.head.appendChild(script);
}
function loadBootstrapCss() {
    const link = document.createElement('link');
    link.href = 'https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css';
    link.rel = 'stylesheet';
    document.head.appendChild(link);
    const link2 = document.createElement('link');
    link2.href = 'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.4.0/font/bootstrap-icons.min.css';
    link2.rel = 'stylesheet';
    document.head.appendChild(link2);
    
}
function chainCallback(object, property, callback) {
    if (object == undefined) {
        return;
    }
    if (property in object) {
        const originalCallback = object[property];
        object[property] = function () {
            const result = originalCallback.apply(this, arguments);
            callback.apply(this, arguments);
            return result;
        };
    } else {
        object[property] = callback;
    }
}

class TimelineWidget {
    constructor(node) {
        this.node = node;
        this.keyframes = [];
        this.widgets = node.widgets;
        this.maxX = 20; // Default maxX
        this.maxY = 100; // Default maxY
        this.prevMaxX = 1; // Previous value of maxX
        this.prevValueRange = 1; 
        this.pointsDisplay = null;
        this.generateButton = null;
        this.deleteButton = null;
        this.generatedKeyframes = [];
        this.createChartContainer();
    }
    
    createChartContainer() {
        this.chartContainer = document.createElement('div');
        this.chartContainer.style.height = '200px';
        this.chartContainer.style.width = '200px';
        this.node.addDOMWidget("Chart", "custom", this.chartContainer, {});
    }

    updateGenerateButtonState() {
        if (this.generateButton != null && this.deleteButton != null){
            this.generateButton.disabled = this.keyframes.length < 2;
            this.deleteButton.disabled = this.generatedKeyframes.length === 0;
        }

    }
    createPointsDisplay() {
        // Ensure pointsDisplay is created and has a defined size
        this.pointsDisplay = document.createElement('div');
        this.pointsDisplay.classList.add('points-display', 'd-flex', 'flex-wrap', 'justify-content-start', 'align-items-center');
        this.pointsDisplay.style.borderRadius = '15px';
        this.pointsDisplay.style.border = '1px solid #C8C8C8';
        this.pointsDisplay.style.backgroundColor = '#353535';
        this.pointsDisplay.style.padding = '10px';
        this.pointsDisplay.style.marginTop = '5px'; // Add some space above the container
        this.pointsDisplay.style.minHeight = '50px'; // Make sure there is enough height for buttons
    
        // Append the points display to the chart container
        this.chartContainer.appendChild(this.pointsDisplay);
    
        // Update the button states accordingly
    }
    createGenerationButton() {
        // Create a container for buttons and the dropdown
        const buttonsContainer = document.createElement('div');
        buttonsContainer.style.width = '100%';
        buttonsContainer.style.display = 'flex';
        buttonsContainer.style.marginBottom = '10px'; 
    
        // Define classes that will be common to buttons and the dropdown
        const commonClassList = ['btn'];
        const commonHeight = '38px';
    
        // Create and append the generate button
        this.generateButton = document.createElement('button');
        this.generateButton.innerText = 'Generate Values';
        this.generateButton.classList.add(...commonClassList, 'btn-secondary');        
        this.generateButton.style.height = commonHeight;
        this.generateButton.style.flex = '1'; // Add this line
        this.generateButton.style.marginRight = '2px'; // Add spacing between elements
        this.generateButton.style.padding = '5px 10px'; // Adjust padding as needed
        this.generateButton.onclick = () => this.generateInBetweenValues();
        // add border radius to the button
        this.generateButton.style.borderRadius = '5px';
        buttonsContainer.appendChild(this.generateButton);
    
        // Create and append the delete button
        this.deleteButton = document.createElement('button');
        this.deleteButton.innerText = 'Delete Generated';
        this.deleteButton.classList.add(...commonClassList, 'btn-danger');
        this.deleteButton.style.height = commonHeight;
        this.deleteButton.style.flex = '1'; // Add this line
        // add border radius to the button
        this.deleteButton.style.borderRadius = '5px';
        this.deleteButton.style.marginRight = '2px'; // Add spacing between elements
        this.deleteButton.style.padding = '5px 10px'; // Adjust padding as needed
        this.deleteButton.onclick = () => this.deleteGeneratedValues();
        buttonsContainer.appendChild(this.deleteButton);
    

        // Create the nterpolation type dropdown

    
        // Append the buttons container to the pointsDisplay
        this.pointsDisplay.appendChild(buttonsContainer);
    
        // Update the button states accordingly
        this.updateGenerateButtonState();
    }
    
    
    updatePointsDisplay() {
        const badges = this.pointsDisplay.querySelectorAll('.badge');
        badges.forEach(badge => badge.remove());
        this.keyframes.forEach((kf, index) => {
            const badge = document.createElement('div');
            badge.classList.add('badge', 'm-1');
            badge.style.border = '1px solid #666666';
            badge.style.borderRadius = '25px';
            badge.style.textAlign = 'center';
            badge.style.paddingLeft = '15px';
            badge.style.paddingRight = '-15px';
            badge.style.color = '#999999';       
            badge.innerHTML = `frame: ${kf.x}, value: ${kf.y}`;
            badge.style.backgroundColor = '#222222';
            badge.style.display = 'flex'; // Add this line
            badge.style.justifyContent = 'center'; // Add this line
            badge.style.alignItems = 'center'; 
            badge.style.height = '30px'; // Adjust the value as needed
            const deleteButton = document.createElement('button');
            deleteButton.classList.add('btn');
            deleteButton.innerHTML = '<i class="bi bi-trash"></i>';
            deleteButton.style.color = '#999999';  
            deleteButton.style.marginLeft = '-15px';
            deleteButton.onclick = () => {
                this.removeChartKeyframe(index);
            };


            // Add an edit button to each badge
            let editButton = document.createElement('button');
            editButton.innerHTML = '<i class="bi bi-pencil"></i>';
            editButton.classList.add('btn');
            
            // add minus padding to the left of the button
            editButton.style.color = '#999999';  
   
            // Store the this value in a variable
            let self = this;
            // Add event listener to the edit button
            editButton.onclick = () => {
                // Get the current frame and value variables of the chart point from the badge's text
                let badgeText = badge.innerText;
                let splitText = badgeText.split(', ');
                let match1 = splitText[0].match(/frame: ([-+]?[0-9]*\.?[0-9]+)/);
                let currentFrame = match1 ? match1[1] : '';
                let match2 = splitText[1].match(/value: ([-+]?[0-9]*\.?[0-9]+)/);
                let currentValue = match2 ? match2[1] : '';

                // Create labels and input fields for the frame and value
                let frameLabel = document.createElement('span');
                frameLabel.innerText = 'frame: ';

                let frameInput = document.createElement('input');
                frameInput.type = 'text';
                frameInput.value = currentFrame;
                frameInput.style.width = '25px'; // Set the width dynamically
                frameInput.style.height = '15px'; // Adjust the value as needed


                let valueLabel = document.createElement('span');
                valueLabel.innerText = 'value: ';

                let valueInput = document.createElement('input');
                valueInput.type = 'text';
                valueInput.value = currentValue;
                valueInput.style.width = '25px'; // Set the width dynamically
                valueInput.style.height = '15px'; // Adjust the value as needed

                // Create a save button
                let saveButton = document.createElement('button');
                saveButton.classList.add('btn');
                saveButton.innerHTML = '<i class="bi bi-check"></i>';
                saveButton.style.color = '#999999';  
                //saveButton.style.marginRight = '20px'; 
                saveButton.firstChild.style.fontSize = '1.5em'; // Adjust the value as needed// Adjust the value as needed   

                // Replace the badge's innerHTML with the labels, input fields, and save button
                badge.innerHTML = '';
                badge.appendChild(frameLabel);
                badge.appendChild(frameInput);
                badge.appendChild(valueLabel);
                badge.appendChild(valueInput);
                badge.appendChild(saveButton);

                // When creating the badge, store the index of the point
                badge.dataset.index = index;

                // Add event listener to the save button
                saveButton.onclick = () => {
                    // Get the new frame and value from the input fields
                    let newFrame = parseFloat(frameInput.value);
                    let newValue = parseFloat(valueInput.value);

                    // Get the index of the old keyframe from the badge
                    let oldIndex = parseInt(badge.dataset.index);

                    // Remove the old keyframe
                    self.removeChartKeyframe(oldIndex);

                    // Add the new keyframe
                    self.addChartKeyframe(newFrame, newValue, oldIndex);

                    // Update the badge's dataset with the new frame and value
                    badge.dataset.frame = newFrame;
                    badge.dataset.value = newValue;

                    // Replace the input fields and save button with the new frame and value
                    badge.innerHTML = `frame: ${newFrame}, value: ${newValue}`;

                    // Append the edit and delete buttons after updating the badge's innerHTML
                    badge.appendChild(editButton);
                    badge.appendChild(deleteButton);
                };
            };

            badge.appendChild(editButton);
            badge.appendChild(deleteButton);
            this.pointsDisplay.appendChild(badge);
        });

    }
    
    generateInBetweenValues() {
        if (this.keyframes.length < 2) return; // Safety check
        
        let easing_type_widget = this.widgets.find(w => w.name === "easing_type").value || "linear";

        // Clear any previously generated keyframes
        this.generatedKeyframes = [];
    
        // Make sure the keyframes are sorted by the frame number
        this.keyframes.sort((a, b) => a.x - b.x);
    
        // The first and the last keyframes should always be part of the generated keyframes
        this.generatedKeyframes.push(this.keyframes[0]);

        // Helper functions for interpolation methods
        const easings = {
            linear: (t, b, c, d) => c * t / d + b,
            easeInQuad: (t, b, c, d) => c * (t /= d) * t + b,
            easeOutQuad: (t, b, c, d) => -c * (t /= d) * (t - 2) + b,
            easeInOutQuad: (t, b, c, d) => {
                t /= d / 2;
                if (t < 1) return c / 2 * t * t + b;
                t--;
                return -c / 2 * (t * (t - 2) - 1) + b;
            },
            easeInCubic: (t, b, c, d) => c * Math.pow(t / d, 3) + b,
            easeOutCubic: (t, b, c, d) => c * (Math.pow(t / d - 1, 3) + 1) + b,
            easeInOutCubic: (t, b, c, d) => {
                t /= d / 2;
                if (t < 1) return c / 2 * Math.pow(t, 3) + b;
                t -= 2;
                return c / 2 * (Math.pow(t, 3) + 2) + b;
            },
            easeInQuart: (t, b, c, d) => c * Math.pow(t / d, 4) + b,
            easeOutQuart: (t, b, c, d) => -c * (Math.pow(t / d - 1, 4) - 1) + b,
            easeInOutQuart: (t, b, c, d) => {
                t /= d / 2;
                if (t < 1) return c / 2 * Math.pow(t, 4) + b;
                t -= 2;
                return -c / 2 * (Math.pow(t, 4) - 2) + b;
            },
            easeInQuint: (t, b, c, d) => c * Math.pow(t / d, 5) + b,
            easeOutQuint: (t, b, c, d) => c * (Math.pow(t / d - 1, 5) + 1) + b,
            easeInOutQuint: (t, b, c, d) => {
                t /= d / 2;
                if (t < 1) return c / 2 * Math.pow(t, 5) + b;
                t -= 2;
                return c / 2 * (Math.pow(t, 5) + 2) + b;
            },
            exponential: (t, b, c, d) => t === 0 ? b : c * Math.pow(2, 10 * (t / d - 1)) + b,
        };

        // Use a default interpolation method if the selected one isn't available
        
        const interpolate = easings[easing_type_widget] || easings.linear;

        // Perform interpolation based on the selected type
        for (let i = 0; i < this.keyframes.length - 1; i++) {
            const startFrame = this.keyframes[i];
            const endFrame = this.keyframes[i + 1];
            const frameDiff = endFrame.x - startFrame.x;
            const valueDiff = endFrame.y - startFrame.y;

            for (let frame = startFrame.x + 1; frame < endFrame.x; frame++) {
                const t = frame - startFrame.x;
                const interpolatedValue = interpolate(t, startFrame.y, valueDiff, frameDiff);
                const roundedValue = Math.round(interpolatedValue);
                this.generatedKeyframes.push({ x: frame, y: roundedValue });
            }

            // Always include the end frame
            this.generatedKeyframes.push(endFrame);

        }
        // Update the chart with two datasets: one for user keyframes, one for generated keyframes
        this.chart.data.datasets = [
            {
                label: 'User Values',
                data: this.keyframes,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0,
                pointRadius: 5,
                pointStyle: 'rectRot',
                showLine: true
            },
            {
                label: 'Generated Values',
                data: this.generatedKeyframes,
                fill: false,
                borderColor: 'rgb(255, 159, 64)',
                tension: 0,
                pointRadius: 5,
                pointStyle: 'circle',
                showLine: true
            }
        ];
        localStorage.setItem('savedGeneratedKeyframes', JSON.stringify(this.generatedKeyframes));
        // Update chart with new data
        this.chart.update();
    
        // Refresh the points display and buttons
        this.updatePointsDisplay();
        this.updateGenerateButtonState();
    }
    
    deleteGeneratedValues() {
        this.generatedKeyframes = [];
            if (this.chart.data.datasets.length > 1) {
            this.chart.data.datasets[1].data = [];
            this.chart.update();
        }
        this.updateGenerateButtonState();
        this.updatePointsDisplay();
    }

    removeChartKeyframe(index) {
        this.keyframes.splice(index, 1);
        this.updateChartData();
        this.updatePointsDisplay();
        this.updateGenerateButtonState();
        if(this.keyframes.length == 0){
            this.chartContainer.removeChild(this.pointsDisplay);
            this.deleteGeneratedValues()
        }
    }
    updateChartData() {
        this.keyframes.sort((a, b) => a.x - b.x);
        this.chart.data.datasets[0].data = this.keyframes.map(kf => ({ x: kf.x, y: kf.y }));

        //this.generatedKeyframes.sort((a, b) => a.x - b.x);
        //this.chart.data.datasets[1].data = this.generatedKeyframes.map(kf => ({ x: kf.x, y: kf.y }));
        this.chart.update();
    }   
        
    updateTicks(maxX, valueRange) {
        this.maxX = maxX;
        this.maxY = Math.abs(valueRange);
        
        if (this.chart) {
            // Capture the current zoom state
            const xScale = this.chart.scales['x'];
            const yScale = this.chart.scales['y'];
            const xMin = xScale.min;
            const xMax = xScale.max;
            const yMin = yScale.min;
            const yMax = yScale.max;
    
            // Update the scales
            this.chart.options.scales.x.max = maxX;
            this.chart.options.scales.y.min = -this.maxY;
            this.chart.options.scales.y.max = this.maxY;
    
            // Sort and update keyframes
            this.keyframes.sort((a, b) => a.x - b.x);
            this.chart.data.datasets[0].data = this.keyframes.map(kf => ({ x: kf.x, y: kf.y }));
    
            // Reapply the zoom state
            xScale.min = xMin;
            xScale.max = xMax;
            yScale.min = yMin;
            yScale.max = yMax;

            this.chart.update();

        }
    }
    updateStepSize(stepSize) {
        if (this.chart) {
            // Adjust the step size of the chart based on the stepSize value
            if (stepSize === 'auto') {
                this.chart.options.scales.x.ticks.autoSkip = true;
                this.chart.options.scales.y.ticks.autoSkip = true;
            } else {
                this.chart.options.scales.x.ticks.autoSkip = false;
                this.chart.options.scales.x.ticks.stepSize = 1;
                this.chart.options.scales.y.ticks.autoSkip = false;
                this.chart.options.scales.y.ticks.stepSize = 1;
            }

            this.chart.update();
        }
    }    
    
    addChartKeyframe(x, y) {    
        const keyframeIndex = this.keyframes.findIndex(kf => kf.x === x);
        if (keyframeIndex > -1) {
            this.keyframes[keyframeIndex].y = y;
        } else {
            this.keyframes.push({ x: x, y: y });
        }
        // Sort and update keyframes
        this.keyframes.sort((a, b) => a.x - b.x);
        this.chart.data.datasets[0].data = this.keyframes.map(kf => ({ x: kf.x, y: kf.y }));
        // Update chart without losing zoom state
        this.chart.update();
        if(this.pointsDisplay != null ) {
            this.updatePointsDisplay();
        }
        else {
            
            this.createPointsDisplay();
            this.createGenerationButton(); 
            this.updatePointsDisplay();

        }
        if(!this.pointsDisplay.parentNode){
            this.chartContainer.appendChild(this.pointsDisplay);
        }

        this.updateGenerateButtonState();
        localStorage.setItem('savedKeyframes', JSON.stringify(this.keyframes));
    }

    calculateValuesFromClick(event, canvas) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const canvasX = (event.clientX - rect.left) * scaleX;
        const canvasY = (event.clientY - rect.top) * scaleY;
        const scales = this.chart.scales;
        const xScaleKey = Object.keys(scales).find(key => scales[key].axis === 'x');
        const yScaleKey = Object.keys(scales).find(key => scales[key].axis === 'y');
        if (!scales[xScaleKey] || !scales[yScaleKey]) {
            console.error('Chart scales not found.');
            return { x: 0, y: 0 };
        }
        const xValue = scales[xScaleKey].getValueForPixel(canvasX);
        const yValue = scales[yScaleKey].getValueForPixel(canvasY);

        if(xValue < 1){
            xValue=1;
        }
        if(xValue > this.maxX){
            xValue = this.maxX;
        }
        return { x: Math.round(xValue), y: Math.round(yValue) };
    }

    initChart(maxX, maxY) {
        this.maxX = maxX;
        this.maxY = maxY;
        const canvas = document.createElement('canvas');

        const data = {
            labels: Array.from({ length: maxX }, (_, i) => i + 1),
            datasets: [{
                label: 'User Values',
                data: this.keyframes,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0,
                pointRadius: 5,
                pointStyle: 'rectRot',
                showLine: true
            },
            {
                label: 'Generated Values',
                data: this.generatedKeyframes,
                fill: false,
                borderColor: 'rgb(255, 159, 64)',
                tension: 0,
                pointRadius: 5,
                pointStyle: 'circle',
                showLine: true
            }]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                maintainAspectRatio: false,
                responsive: true,
                layout: {
                    padding: {
                        right: 45 
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        min: 1,
                        max: Math.round(maxX),
                        ticks: {
                            callback: function(value) {
                                if (Math.floor(value) === value) {
                                    return value;
                                }
                            },
                            
                            stepSize: 1,
                            autoSkip: false,
                            
                        },
                        title: {
                            display: true,
                            text: 'frames' // Replace with your x-axis label
                        }
                    },
                    y: {
                        min: -maxY, // Set initial minimum value for y-axis
                        max: maxY, // Set initial maximum value for y-axis
                        ticks: {
                            callback: function(value) {
                                if (Math.floor(value) === value) {
                                    return value;
                                }
                            },
                            
                            stepSize: 1, // Use the dynamic step size
                            autoSkip: false
                        },
                        title: {
                            display: true,
                            text: 'values'
                        },
                    }
                },
                plugins: {
                    tooltip: {
                        enabled: true, 
                        callbacks: {
                            label: function(context) {
                                return `frame = ${context.label}, value = ${context.parsed.y}`;
                            },
                            title: function() {
                                return 'scheduled value'; // Replace with your desired title
                            }                        
                        }
                    },
                    zoom: {
                        zoom: {
                            wheel: {
                                speed: 0.1,
                                enabled: true,
                            },
                            mode: 'y',
                            minInterval: 1,
                            onZoom: (context) => {
                                const chart = context.chart;
                                if (!chart || !chart.scales) {
                                    console.error('Chart or chart scales not found.');
                                    return;
                                }
                                
                                const yScale = chart.scales['y'];
                                yScale.options.ticks.min = Math.round(yScale.min);
                                yScale.options.ticks.max = Math.round(yScale.max);
                            }
                        }
                    }
                }
            }
        };

        this.chartContainer.appendChild(canvas);
        
        this.chart = new Chart(canvas.getContext('2d'), config);


        canvas.addEventListener('click', (event) => {
            const { x, y } = this.calculateValuesFromClick(event, canvas);
            this.addChartKeyframe(x, y);
        });

    }

}

app.registerExtension({
    name: "ManaNodes.scheduled_values",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "scheduled_values") {

            // Restoring state in onConfigure
            chainCallback(nodeType.prototype, "onConfigure", function () {
                const savedKeyframes = JSON.parse(localStorage.getItem('savedKeyframes'));
                const savedGeneratedKeyframes = JSON.parse(localStorage.getItem('savedGeneratedKeyframes'));
                

                if (savedKeyframes) {
                    console.log('gesavedKeyframeslp',savedKeyframes);
                    this.timelineWidget.keyframes = savedKeyframes;
                }

                if (savedGeneratedKeyframes) {
                    console.log('savedGeneratedKeyframes',savedGeneratedKeyframes);
                    this.timelineWidget.generatedKeyframes = savedGeneratedKeyframes;

                }
            });

            chainCallback(nodeType.prototype, 'onNodeCreated', function () {
                const frame_count_widget = this.widgets.find(w => w.name === "frame_count");
                const value_range_widget = this.widgets.find(w => w.name === "value_range");

                let maxX = frame_count_widget ? parseInt(frame_count_widget.value, 10) : 20;
                let valueRange = value_range_widget ? parseInt(value_range_widget.value, 10) : 100;
                
                const timelineWidget = new TimelineWidget(this);
                loadChartJs(() => {
                    timelineWidget.initChart(maxX, valueRange);
                });
                loadBootstrapCss();
                this.timelineWidget = timelineWidget;

            });

            chainCallback(nodeType.prototype, 'onDrawBackground', function () {
                const frame_count_widget = this.widgets.find(w => w.name === "frame_count");
                const value_range_widget = this.widgets.find(w => w.name === "value_range");
                let maxX = frame_count_widget ? parseInt(frame_count_widget.value, 10) : 20;
                let valueRange = value_range_widget ? parseInt(value_range_widget.value, 10) : 100;
                const step_size_widget = this.widgets.find(w => w.name === "step_mode");
                let stepSize = step_size_widget ? step_size_widget.value : "single";

                if (this.prevMaxX !== maxX || this.prevValueRange !== valueRange) {
                    if (this.timelineWidget) {
                        this.timelineWidget.updateTicks(maxX, valueRange);
                    }
                    this.prevMaxX = maxX;
                    this.prevValueRange = valueRange;
                } 

                if (this.stepSize !== stepSize) {
                    if (this.timelineWidget) {
                        this.timelineWidget.updateStepSize(stepSize);
                    }
                    this.stepSize = stepSize;
                } 



                if (this.timelineWidget) {
                    // Combine keyframes and generatedKeyframes.
                    let combinedKeyframes = [...this.timelineWidget.keyframes, ...this.timelineWidget.generatedKeyframes];
                
                    // Sort combined array based on 'x' to ensure order.
                    combinedKeyframes.sort((a, b) => a.x - b.x);
                
                    // Remove duplicates.
                    const uniqueKeyframes = Array.from(new Map(combinedKeyframes.map(kf => [kf.x, kf])).values());
                
                    // Set the value for the widget.
                    this.widgets.find(w => w.name === "scheduled_values").value = JSON.stringify(uniqueKeyframes);
                }
            });
        }
    },
});
