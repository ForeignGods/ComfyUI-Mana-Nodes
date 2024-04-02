import { app } from "../../../scripts/app.js";

function loadChartJs(callback) {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = () => {
        const pluginScript = document.createElement('script');
        pluginScript.src = 'https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@1.0.1/dist/chartjs-plugin-zoom.min.js';
        pluginScript.onload = callback; // Call the callback once the plugin is loaded
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
        this.maxX = 20; // Default maxX
        this.maxY = 100; // Default maxY
        this.prevMaxX = 1; // Previous value of maxX
        this.prevValueRange = 1; 
        this.pointsDisplay = null;
        this.generateButton = null;
        this.deleteButton = null;
        this.generatedKeyframes = []; // New array to hold generated in-between keyframes
        this.createChartContainer();
        //this.createPointsDisplay();
    }
    
    createChartContainer() {
        this.chartContainer = document.createElement('div');
        this.chartContainer.style.height = '200px';
        this.chartContainer.style.width = '200px';
        //this.chartContainer.style.overflow = 'auto'; // Enable scrolling
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
        buttonsContainer.classList.add('d-flex');
        buttonsContainer.style.width = '100%'; // Ensure container fills the line
        buttonsContainer.style.marginBottom = '10px'; // Ensure container fills the line
    
        // Define classes that will be common to buttons and the dropdown
        const commonClassList = ['btn'];
        const commonHeight = '38px';
    
        // Create and append the generate button
        this.generateButton = document.createElement('button');
        this.generateButton.innerText = 'Generate In-betweens';
        this.generateButton.classList.add(...commonClassList, 'btn-secondary');        
        this.generateButton.style.height = commonHeight;
        this.generateButton.style.marginRight = '2px'; // Add spacing between elements
        this.generateButton.style.padding = '5px 10px'; // Adjust padding as needed
        this.generateButton.style.width = '400px'; // Adjust padding as needed
        this.generateButton.onclick = () => this.generateInBetweenValues();
        buttonsContainer.appendChild(this.generateButton);
    
        // Create and append the delete button
        this.deleteButton = document.createElement('button');
        this.deleteButton.innerText = 'Delete Generated';
        this.deleteButton.classList.add(...commonClassList, 'btn-danger');
        this.deleteButton.style.height = commonHeight;
        this.deleteButton.style.marginRight = '2px'; // Add spacing between elements
        this.deleteButton.style.padding = '5px 10px'; // Adjust padding as needed
        this.deleteButton.style.width = '400px'; // Adjust padding as needed
        this.deleteButton.onclick = () => this.deleteGeneratedValues();
        buttonsContainer.appendChild(this.deleteButton);
    
        // Create the interpolation type dropdown
        this.interpolationTypeSelect = document.createElement('select');
        this.interpolationTypeSelect.classList.add(...commonClassList,'custom-select');
        this.interpolationTypeSelect.style.height = commonHeight;
        this.interpolationTypeSelect.style.marginLeft = 'auto'; // Push the dropdown to the end of the container
    
        const interpolationOptions = {
            linear: 'Linear',
            easeInQuad: 'Ease In Quad',
            easeOutQuad: 'Ease Out Quad',
            easeInOutQuad: 'Ease In-Out Quad',
            easeInCubic: 'Ease In Cubic',
            easeOutCubic: 'Ease Out Cubic',
            easeInOutCubic: 'Ease In-Out Cubic',
            easeInQuart: 'Ease In Quart',
            easeOutQuart: 'Ease Out Quart',
            easeInOutQuart: 'Ease In-Out Quart',
            easeInQuint: 'Ease In Quint',
            easeOutQuint: 'Ease Out Quint',
            easeInOutQuint: 'Ease In-Out Quint',
            exponential: 'Exponential',
            // Add more types here
        };
        
        // Iterate over the interpolationOptions to create and append the option elements
        for (const [value, text] of Object.entries(interpolationOptions)) {
        const optionElement = document.createElement('option');
        optionElement.value = value;
        optionElement.text = text;
        this.interpolationTypeSelect.appendChild(optionElement);
        }

        // Append the dropdown to the buttonsContainer
        buttonsContainer.appendChild(this.interpolationTypeSelect);
    
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
            badge.style.border = '1px solid #666666'; // Adding a white border
            badge.style.borderRadius = '25px'; // Adding a white border
            badge.style.textAlign = 'center'; // Adding a white border
            badge.style.paddingLeft = '15px'; // Padding similar to frame_count widget
            badge.style.paddingRight = '-15px'; // Padding similar to frame_count widget
            badge.style.color = '#999999'; // White text color            
            badge.innerHTML = `frame: ${kf.x}, value: ${kf.y}`;
            badge.style.backgroundColor = '#222222'; // Green background color

            const deleteButton = document.createElement('button');
            deleteButton.classList.add('btn');
            deleteButton.innerHTML = '<i class="bi bi-trash"></i>'; // Bootstrap icon
            deleteButton.style.color = '#999999'; // White text color       
            deleteButton.onclick = () => {
                this.removeChartKeyframe(index);
            };

            badge.appendChild(deleteButton);
            this.pointsDisplay.appendChild(badge);
        });

    }
    
    generateInBetweenValues() {
        if (this.keyframes.length < 2) return; // Safety check
    
        // Get the selected interpolation type from the dropdown
        const interpolationType = this.interpolationTypeSelect.value;
    
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
        const interpolate = easings[interpolationType] || easings.linear;

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
                label: 'User Keyframes',
                data: this.keyframes,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0,
                pointRadius: 5,
                pointStyle: 'rectRot',
                showLine: true
            },
            {
                label: 'Generated In-Betweens',
                data: this.generatedKeyframes,
                fill: false,
                borderColor: 'rgb(255, 159, 64)',
                tension: 0,
                pointRadius: 5,
                pointStyle: 'circle',
                showLine: true
            }
        ];
    
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
        this.chart.update();
    }   

    updateChart(maxX, valueRange) {
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
        return { x: Math.round(xValue), y: Math.round(yValue) };
    }

    initChart(maxX, maxY) {
        this.maxX = maxX;
        this.maxY = maxY;
        const canvas = document.createElement('canvas');

        const data = {
            labels: Array.from({ length: maxX }, (_, i) => i + 1),
            datasets: [{
                label: 'User Keyframes',
                data: this.keyframes,
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0,
                pointRadius: 5,
                pointStyle: 'rectRot',
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
                            autoSkip: false
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
                            stepSize: 1,
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
                if (this.prevMaxX !== maxX || this.prevValueRange !== valueRange) {
                    if (this.timelineWidget) {
                        this.timelineWidget.updateChart(maxX, valueRange);
                    }
                    this.prevMaxX = maxX;
                    this.prevValueRange = valueRange;
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
