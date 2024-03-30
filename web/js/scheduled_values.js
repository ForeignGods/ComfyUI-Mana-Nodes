import { app } from "../../../scripts/app.js";

function loadChartJs(callback) {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    script.onload = () => {
        // Load the plugin after Chart.js is loaded
        const pluginScript = document.createElement('script');
        pluginScript.src = 'https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@1.0.1/dist/chartjs-plugin-zoom.min.js';
        pluginScript.onload = callback; // Call the callback once the plugin is loaded
        document.head.appendChild(pluginScript);
    };
    document.head.appendChild(script);
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
        this.createChartContainer();
    }

    createChartContainer() {
        console.log("Creating chart container");
        this.chartContainer = document.createElement('div');
        this.chartContainer.style.height = '200px';
        this.chartContainer.style.border = '1px solid gray';
        this.chartContainer.style.overflow = 'auto'; // Enable scrolling
        this.node.addDOMWidget("Chart", "custom", this.chartContainer, {});
    }

    initChart(maxX, maxY) {
        this.maxX = maxX;
        this.maxY = maxY;
        const canvas = document.createElement('canvas');
        this.chartContainer.appendChild(canvas);

        const data = {
            labels: Array.from({ length: maxX }, (_, i) => i + 1),
            datasets: [{
                label: 'Keyframes',
                data: [],
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
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
                        }
                    },
                    y: {
                        ticks: {
                            callback: function(value) {
                                if (Math.floor(value) === value) {
                                    return value;
                                }
                            },
                            stepSize: 1,
                        }
                    }
                },
                plugins: {
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

        this.chart = new Chart(canvas.getContext('2d'), config);
        canvas.addEventListener('click', (event) => {
            console.log("Canvas clicked");
            const { x, y } = this.calculateValuesFromClick(event, canvas);
            console.log(`Click coordinates: x=${x}, y=${y}`);
            this.addChartKeyframe(x, y);
        });
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
        console.log(`Adding/updating keyframe at x: ${x}, y: ${y}`);
    
    
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
}

app.registerExtension({
    name: "ManaNodes.scheduled_values",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === "scheduled_values") {
            chainCallback(nodeType.prototype, 'onNodeCreated', function () {
                const timelineWidget = new TimelineWidget(this);
                loadChartJs(() => {
                    timelineWidget.initChart(20, 100);
                });
                this.timelineWidget = timelineWidget;
            });

            chainCallback(nodeType.prototype, 'onDrawBackground', function () {
                console.log('drawBackground');
                const frame_count_widget = this.widgets.find(w => w.name === "frame_count");
                const value_range_widget = this.widgets.find(w => w.name === "value_range");
                let maxX = frame_count_widget ? parseInt(frame_count_widget.value, 10) : 20;
                let valueRange = value_range_widget ? parseInt(value_range_widget.value, 10) : 100;
                if (this.prevMaxX !== maxX || this.prevValueRange !== valueRange) {
                    console.log('drawBackground update chart');
                    if (this.timelineWidget) {
                        this.timelineWidget.updateChart(maxX, valueRange);
                    }
                    this.prevMaxX = maxX;
                    this.prevValueRange = valueRange;
                }
            });
            // Other chained callbacks...
        }
    },
});
