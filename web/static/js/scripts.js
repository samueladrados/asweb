/*!
    * Start Bootstrap - SB Admin v7.0.7 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2023 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

var wordEmbeddings = [];


const word_embeddings_loaded = document.getElementById("word_embeddings_loaded");


const save_word_embedding_button = document.getElementById("save_word_embedding");
const delete_word_embedding_button = document.getElementById("delete_word_embedding");
const select_we = document.getElementById("select_we");
const select_we_1 = document.getElementById("select_we_1");
const select_we_2 = document.getElementById("select_we_2");
const select_measurement_method = document.getElementById("select_measurement_method");
const select_debiasing = document.getElementById("select_debiasing");
const select_direction = document.getElementById("select_direction");
const div_debiasing_options = document.getElementById("div_debiasing_options");
const button_debiasing_options = document.getElementById("button_debiasing_options");
const div_visualization = document.getElementById("div_visualization")
const div_measurements_options = document.getElementById("div_measurements_options");
const button_measurements = document.getElementById("button_measurements");
const table_body = document.getElementById("table_body");
const myTable = document.getElementById("datatablesSimple")
const dataTable = new simpleDatatables.DataTable(myTable);


//Create SVG for visualization
function createSVG(data, id, vector_data, direction_name, name, text_ejex, text_ejey) {

    var margin = { top: 50, right: 30, bottom: 60, left: 70 };
    var width = 600 - margin.left - margin.right;
    var height = 600 - margin.top - margin.bottom;

    var svg = d3.select("#"+id)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    var xScale = d3.scaleLinear()
        .domain([-1.15, 1.15])
        .range([0, width]);

    var yScale = d3.scaleLinear()
        .domain([-1.15, 1.15])
        .range([height, 0]);


    var colorScale = d3.scaleOrdinal()
        .domain(['female', 'male', 'neutral'])
        .range(['#FF69B4', '#0000FF', '#008000']);


    var circles = svg.selectAll("circle")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", function (d) { return xScale(d.x); })
        .attr("cy", function (d) { return yScale(d.y); })
        .attr("r", 5)
        .style("fill", function (d) { return colorScale(d.group); });

    var labels = svg.selectAll("text")
        .data(data)
        .enter()
        .append("text")
        .attr("x", function (d) { return xScale(d.x) + 5; })
        .attr("y", function (d) { return yScale(d.y) - 5; })
        .text(function (d) { return d.label; })
        .style("font-size", "12px");

    svg.append("text")
        .attr("x", width / 2)
        .attr("y", -10)
        .text(name)
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .style("font-weight", "bold");

    var xAxis = d3.axisBottom(xScale);
    var yAxis = d3.axisLeft(yScale);


    svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);


    svg.append("g")
        .attr("class", "y-axis")
        .call(yAxis);


    svg.append("text")
        .attr("class", "x-axis-label")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom / 2)
        .text(text_ejex)
        .attr("text-anchor", "middle")
        .style("font-size", "12px");

    svg.append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("x", -height / 2)
        .attr("y", -margin.left / 2)
        .text(text_ejey)
        .attr("text-anchor", "middle")
        .style("font-size", "12px");


    var legend = svg.selectAll(".legend")
        .data(colorScale.domain())
        .enter()
        .append("g")
        .attr("class", "legend")
        .attr("transform", function (d, i) { return "translate(" + i * 80 + "," + (height + 40) + ")"; });

    legend.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", 10)
        .attr("height", 10)
        .style("fill", function (d) { return colorScale(d); });

    legend.append("text")
        .attr("x", 15)
        .attr("y", 9)
        .text(function (d) { return d; })
        .style("font-size", "12px");

    if (direction_name != null || vector_data != null) {
        if (vector_data[1].x != 0 || vector_data[1].y != 0) {
            var line = d3.line()
                .x(function (d) { return xScale(d.x); })
                .y(function (d) { return yScale(d.y); });

            svg.append("path")
                .datum(vector_data)
                .attr("class", "vector")
                .attr("d", line)
                .style("stroke", "black")
                .style("stroke-width", 2)
                .style("fill", "none");

            svg.append("text")
                .attr("x", xScale(vector_data[0].x) + 5)
                .attr("y", yScale(vector_data[0].y) + 15)
                .text(direction_name)
                .style("font-size", "12px");



            if (vector_data[0].y === vector_data[1].y) {

                svg.append("line")
                    .attr("class", "line-dotted")
                    .attr("x1", xScale(vector_data[0].x))
                    .attr("y1", yScale(-1))
                    .attr("x2", xScale(vector_data[0].x))
                    .attr("y2", yScale(1))
                    .style("stroke-dasharray", "3,3")
                    .style("stroke", "black");
            } else {


            }
        } else {
            svg.append("circle")
                .attr("cx", xScale(0))
                .attr("cy", yScale(0))
                .attr("r", 5)
                .style("fill", 'black');

            svg.append("text")
                .attr("x", xScale(0) + 5)
                .attr("y", yScale(0) + 5)
                .text(direction_name)
                .style("font-size", "12px");
        }
    }
}



//Create visualization of the points
function create_visualization(data, name, type) {
    while (div_visualization.firstChild) {
        div_visualization.removeChild(div_visualization.firstChild);
    }
    if (type == 'hard' || type == 'soft' || type=='linear') {
        //If type is hard or soft
        var div = document.createElement("div");
        div.className = "row";
        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "Before debiasing";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_1";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);

        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "Before debiasing, with gender direction as x";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_2";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);
        div_visualization.appendChild(div);


        var div = document.createElement("div");
        div.className = "row";
        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "After debiasing, with gender direction as x";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_3";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);


        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "After debiasing";;
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_4";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);
        div_visualization.appendChild(div);


        var dataSVG = [];
        for (var word in data[0]['fem']) {
            dataSVG.push({ x: data[0]['fem'][word]['x'], y: data[0]['fem'][word]['y'], group: 'female', label: data[0]['fem'][word]['label'] });
        }
        for (var word in data[0]['masc']) {
            dataSVG.push({ x: data[0]['masc'][word]['x'], y: data[0]['masc'][word]['y'], group: 'male', label: data[0]['masc'][word]['label'] });
        }
        for (var word in data[0]['neutral']) {
            dataSVG.push({ x: data[0]['neutral'][word]['x'], y: data[0]['neutral'][word]['y'], group: 'neutral', label: data[0]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[0]['gender_direction']) {
            vectorDataSVG.push({ x: data[0]['gender_direction'][word]['x'], y: data[0]['gender_direction'][word]['y'] });
        }


        createSVG(dataSVG, "visualization_1", vectorDataSVG, "gender_direction", name, "PCA's First Component", "PCA's Second Component");


        var dataSVG = [];
        for (var word in data[1]['fem']) {
            dataSVG.push({ x: data[1]['fem'][word]['x'], y: data[1]['fem'][word]['y'], group: 'female', label: data[1]['fem'][word]['label'] });
        }
        for (var word in data[1]['masc']) {
            dataSVG.push({ x: data[1]['masc'][word]['x'], y: data[1]['masc'][word]['y'], group: 'male', label: data[1]['masc'][word]['label'] });
        }
        for (var word in data[1]['neutral']) {
            dataSVG.push({ x: data[1]['neutral'][word]['x'], y: data[1]['neutral'][word]['y'], group: 'neutral', label: data[1]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[1]['gender_direction']) {
            vectorDataSVG.push({ x: data[1]['gender_direction'][word]['x'], y: data[1]['gender_direction'][word]['y'] });
        }
        createSVG(dataSVG, "visualization_2", vectorDataSVG, "gender_direction", name, "Gender Direction (cosine similarity)", "PCA's First Component");




        var dataSVG = [];
        for (var word in data[2]['fem']) {
            dataSVG.push({ x: data[2]['fem'][word]['x'], y: data[2]['fem'][word]['y'], group: 'female', label: data[2]['fem'][word]['label'] });
        }
        for (var word in data[2]['masc']) {
            dataSVG.push({ x: data[2]['masc'][word]['x'], y: data[2]['masc'][word]['y'], group: 'male', label: data[2]['masc'][word]['label'] });
        }
        for (var word in data[2]['neutral']) {
            dataSVG.push({ x: data[2]['neutral'][word]['x'], y: data[2]['neutral'][word]['y'], group: 'neutral', label: data[2]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[2]['gender_direction']) {
            vectorDataSVG.push({ x: data[2]['gender_direction'][word]['x'], y: data[2]['gender_direction'][word]['y'] });
        }
        createSVG(dataSVG, "visualization_3", vectorDataSVG, "gender_direction", name, "Gender Direction (cosine similarity)", "PCA's First Component");



        var dataSVG = [];
        for (var word in data[3]['fem']) {
            dataSVG.push({ x: data[3]['fem'][word]['x'], y: data[3]['fem'][word]['y'], group: 'female', label: data[3]['fem'][word]['label'] });
        }
        for (var word in data[3]['masc']) {
            dataSVG.push({ x: data[3]['masc'][word]['x'], y: data[3]['masc'][word]['y'], group: 'male', label: data[3]['masc'][word]['label'] });
        }
        for (var word in data[3]['neutral']) {
            dataSVG.push({ x: data[3]['neutral'][word]['x'], y: data[3]['neutral'][word]['y'], group: 'neutral', label: data[3]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[3]['gender_direction']) {
            vectorDataSVG.push({ x: data[3]['gender_direction'][word]['x'], y: data[3]['gender_direction'][word]['y'] });
        }
        createSVG(dataSVG, "visualization_4", vectorDataSVG, "gender_direction", name, "PCA's First Component", "PCA's Second Component");


    } else if (type == 'attract' || type == 'nullspace') {
        //If type is attract
        var div = document.createElement("div");
        div.className = "row";
        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "Before debiasing";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_1";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);

        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "After debiasing";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_2";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);
        div_visualization.appendChild(div);

        var dataSVG = [];
        for (var word in data[0]['fem']) {
            dataSVG.push({ x: data[0]['fem'][word]['x'], y: data[0]['fem'][word]['y'], group: 'female', label: data[0]['fem'][word]['label'] });
        }
        for (var word in data[0]['masc']) {
            dataSVG.push({ x: data[0]['masc'][word]['x'], y: data[0]['masc'][word]['y'], group: 'male', label: data[0]['masc'][word]['label'] });
        }
        for (var word in data[0]['neutral']) {
            dataSVG.push({ x: data[0]['neutral'][word]['x'], y: data[0]['neutral'][word]['y'], group: 'neutral', label: data[0]['neutral'][word]['label'] });
        }



        createSVG(dataSVG, "visualization_1", null, null, name, "PCA's First Component", "PCA's Second Component");


        var dataSVG = [];
        for (var word in data[1]['fem']) {
            dataSVG.push({ x: data[1]['fem'][word]['x'], y: data[1]['fem'][word]['y'], group: 'female', label: data[1]['fem'][word]['label'] });
        }
        for (var word in data[1]['masc']) {
            dataSVG.push({ x: data[1]['masc'][word]['x'], y: data[1]['masc'][word]['y'], group: 'male', label: data[1]['masc'][word]['label'] });
        }
        for (var word in data[1]['neutral']) {
            dataSVG.push({ x: data[1]['neutral'][word]['x'], y: data[1]['neutral'][word]['y'], group: 'neutral', label: data[1]['neutral'][word]['label'] });
        }


        createSVG(dataSVG, "visualization_2", null, null, name, "PCA's First Component", "PCA's Second Component");



    } else if (type == 'double') {
        //If type is double
        var div = document.createElement("div");
        div.className = "row";
        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "Before debiasing";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_1";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);

        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "Before debiasing the frecuency direction, with frequency direction as x";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_2";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);
        div_visualization.appendChild(div);



        var div = document.createElement("div");
        div.className = "row";
        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "After debiasing the frecuency direction, with frecuency direction as x";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_3";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);

        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "Before debiasing the gender direction, with gender direction as x";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_4";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);
        div_visualization.appendChild(div);



        var div = document.createElement("div");
        div.className = "row";
        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "After debiasing the gender direction, with gender direction as x";;
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_5";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);

        var div2 = document.createElement("div");
        div2.className = "col-xl-6";
        var div3 = document.createElement("div");
        div3.className = "card mb-4"
        var div4 = document.createElement("div");
        div4.className = "card-header";
        var img = document.createElement("img");
        img.className = "me-1";
        img.src = "static/assets/graph1.png";
        img.style.cssText = "vertical-align: -0.125em; width: 15px; height: 15px;";
        div4.appendChild(img);
        div4.innerHTML += "After debiasing";
        div3.appendChild(div4);
        var div5 = document.createElement("div");
        div5.className = "card-body";
        var div6 = document.createElement("div");
        div6.id = "visualization_6";
        div6.width = "100%";
        div6.height = "40%";
        div5.appendChild(div6);
        div3.appendChild(div5);
        div2.appendChild(div3);
        div.appendChild(div2);
        div_visualization.appendChild(div);


        var dataSVG = [];
        for (var word in data[0]['fem']) {
            dataSVG.push({ x: data[0]['fem'][word]['x'], y: data[0]['fem'][word]['y'], group: 'female', label: data[0]['fem'][word]['label'] });
        }
        for (var word in data[0]['masc']) {
            dataSVG.push({ x: data[0]['masc'][word]['x'], y: data[0]['masc'][word]['y'], group: 'male', label: data[0]['masc'][word]['label'] });
        }
        for (var word in data[0]['neutral']) {
            dataSVG.push({ x: data[0]['neutral'][word]['x'], y: data[0]['neutral'][word]['y'], group: 'neutral', label: data[0]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[0]['frequency_direction']) {
            vectorDataSVG.push({ x: data[0]['frequency_direction'][word]['x'], y: data[0]['frequency_direction'][word]['y'] });
        }
        createSVG(dataSVG, "visualization_1", vectorDataSVG, "frequency_direction", name, "PCA's First Component", "PCA's Second Component");



        var dataSVG = [];
        for (var word in data[1]['fem']) {
            dataSVG.push({ x: data[1]['fem'][word]['x'], y: data[1]['fem'][word]['y'], group: 'female', label: data[1]['fem'][word]['label'] });
        }
        for (var word in data[1]['masc']) {
            dataSVG.push({ x: data[1]['masc'][word]['x'], y: data[1]['masc'][word]['y'], group: 'male', label: data[1]['masc'][word]['label'] });
        }
        for (var word in data[1]['neutral']) {
            dataSVG.push({ x: data[1]['neutral'][word]['x'], y: data[1]['neutral'][word]['y'], group: 'neutral', label: data[1]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[1]['frequency_direction']) {
            vectorDataSVG.push({ x: data[1]['frequency_direction'][word]['x'], y: data[1]['frequency_direction'][word]['y'] });
        }
        createSVG(dataSVG, "visualization_2", vectorDataSVG, "frequency_direction", name, "Frequency Direction (cosine similarity)", "PCA's First Component");



        var dataSVG = [];
        for (var word in data[2]['fem']) {
            dataSVG.push({ x: data[2]['fem'][word]['x'], y: data[2]['fem'][word]['y'], group: 'female', label: data[2]['fem'][word]['label'] });
        }
        for (var word in data[2]['masc']) {
            dataSVG.push({ x: data[2]['masc'][word]['x'], y: data[2]['masc'][word]['y'], group: 'male', label: data[2]['masc'][word]['label'] });
        }
        for (var word in data[2]['neutral']) {
            dataSVG.push({ x: data[2]['neutral'][word]['x'], y: data[2]['neutral'][word]['y'], group: 'neutral', label: data[2]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[2]['frequency_direction']) {
            vectorDataSVG.push({ x: data[2]['frequency_direction'][word]['x'], y: data[2]['frequency_direction'][word]['y'] });
        }
        createSVG(dataSVG, "visualization_3", vectorDataSVG, "frequency_direction", name, "Frequency Direction (cosine similarity)", "PCA's First Component");




        var dataSVG = [];
        for (var word in data[3]['fem']) {
            dataSVG.push({ x: data[3]['fem'][word]['x'], y: data[3]['fem'][word]['y'], group: 'female', label: data[3]['fem'][word]['label'] });
        }
        for (var word in data[3]['masc']) {
            dataSVG.push({ x: data[3]['masc'][word]['x'], y: data[3]['masc'][word]['y'], group: 'male', label: data[3]['masc'][word]['label'] });
        }
        for (var word in data[3]['neutral']) {
            dataSVG.push({ x: data[3]['neutral'][word]['x'], y: data[3]['neutral'][word]['y'], group: 'neutral', label: data[3]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[3]['gender_direction']) {
            vectorDataSVG.push({ x: data[3]['gender_direction'][word]['x'], y: data[3]['gender_direction'][word]['y'] });
        }
        createSVG(dataSVG, "visualization_4", vectorDataSVG, "gender_direction", name, "Gender Direction (cosine similarity)", "PCA's First Component");



        var dataSVG = [];
        for (var word in data[4]['fem']) {
            dataSVG.push({ x: data[4]['fem'][word]['x'], y: data[4]['fem'][word]['y'], group: 'female', label: data[4]['fem'][word]['label'] });
        }
        for (var word in data[4]['masc']) {
            dataSVG.push({ x: data[4]['masc'][word]['x'], y: data[4]['masc'][word]['y'], group: 'male', label: data[4]['masc'][word]['label'] });
        }
        for (var word in data[4]['neutral']) {
            dataSVG.push({ x: data[4]['neutral'][word]['x'], y: data[4]['neutral'][word]['y'], group: 'neutral', label: data[4]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[4]['gender_direction']) {
            vectorDataSVG.push({ x: data[4]['gender_direction'][word]['x'], y: data[4]['gender_direction'][word]['y'] });
        }
        createSVG(dataSVG, "visualization_5", vectorDataSVG, "gender_direction", name, "Gender Direction (cosine similarity)", "PCA's First Component");


        var dataSVG = [];
        for (var word in data[5]['fem']) {
            dataSVG.push({ x: data[5]['fem'][word]['x'], y: data[5]['fem'][word]['y'], group: 'female', label: data[5]['fem'][word]['label'] });
        }
        for (var word in data[5]['masc']) {
            dataSVG.push({ x: data[5]['masc'][word]['x'], y: data[5]['masc'][word]['y'], group: 'male', label: data[5]['masc'][word]['label'] });
        }
        for (var word in data[5]['neutral']) {
            dataSVG.push({ x: data[5]['neutral'][word]['x'], y: data[5]['neutral'][word]['y'], group: 'neutral', label: data[5]['neutral'][word]['label'] });
        }

        var vectorDataSVG = [];
        for (var word in data[5]['gender_direction']) {
            vectorDataSVG.push({ x: data[5]['gender_direction'][word]['x'], y: data[5]['gender_direction'][word]['y'] });
        }
        createSVG(dataSVG, "visualization_6", vectorDataSVG, "gender_direction", name, "PCA's First Component", "PCA's Second Component");
    }
}


//Click button run in debiasing options
const click_button_debiasing_options = (event) => {
    event.preventDefault();
    loading.style.visibility = "visible";


    var message = {}
    message['name'] = select_we.value;
    //HARD DEBIASING
    if (select_debiasing.value == 'hard') {
        message['gender_specific_words'] = document.getElementById('gender_specific_words').value;
        message['gender_neutral_words'] = document.getElementById('gender_neutral_words').value;
        if (select_direction.value == 'pca') {
            message['gender_direction'] = 'pca';
            message['pairs'] = document.getElementById('pairs').value;

        } else if (select_direction.value == 'two_means') {
            message['gender_direction'] = 'two_means';
            message['female_words_direction'] = document.getElementById('female_words_direction').value;
            message['male_words_direction'] = document.getElementById('male_words_direction').value;
        }

        $.ajax({
            type: 'POST',
            url: '/hard',
            data: JSON.stringify(message),
            success: function (data) {
                console.log(data);
                wordEmbeddings.push(data[0]);
                var div2 = document.createElement("div");
                div2.className = "cat action";
                var img = document.createElement("img");
                img.className = "sb-nav-link-icon";
                img.src = "static/assets/embed.png";
                img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
                div2.appendChild(img);
                var label = document.createElement("label");
                label.style.verticalAlign = "middle";
                var input = document.createElement("input");
                input.type = "checkbox";
                input.id = data[0]['name'];
                input.addEventListener("click", check_word_embedding_loaded);
                label.appendChild(input);
                var span = document.createElement("span");
                span.innerHTML += data[0]['name'] + ": n_words=" + data[0]['num_words'] + ", vec_size=" + data[0]['vector_size'];
                label.appendChild(span);
                div2.appendChild(label);
                word_embeddings_loaded.appendChild(div2);
                add_option_we_selections(data[0]['name'], data[0]['num_words'], data[0]['vector_size']);

                var data0=data.shift();

                create_visualization(data, data0['name'], 'hard');

                loading.style.visibility = 'hidden';


            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error hard debiasing.")
            },
            contentType: "application/json",
            dataType: 'json'
        });


    //SOFT DEBIASING
    } else if (select_debiasing.value == 'soft') {
        message['male_words'] = document.getElementById('male_words').value;
        message['female_words'] = document.getElementById('female_words').value;
        message['landa'] = document.getElementById('landa').value;
        message['epochs'] = document.getElementById('epochs').value;
        message['lr'] = document.getElementById('lr').value;
        message['momentum'] = document.getElementById('momentum').value;
        message['gender_neutral_words'] = document.getElementById('gender_neutral_words').value;
        if (select_direction.value == 'pca') {
            message['gender_direction'] = 'pca';
            message['pairs'] = document.getElementById('pairs').value;

        } else if (select_direction.value == 'two_means') {
            message['gender_direction'] = 'two_means';
            message['female_words_direction'] = document.getElementById('female_words_direction').value;
            message['male_words_direction'] = document.getElementById('male_words_direction').value;
        }

        $.ajax({
            type: 'POST',
            url: '/soft',
            data: JSON.stringify(message),
            success: function (data) {
                console.log(data);
                wordEmbeddings.push(data[0]);
                var div2 = document.createElement("div");
                div2.className = "cat action";
                var img = document.createElement("img");
                img.className = "sb-nav-link-icon";
                img.src = "static/assets/embed.png";
                img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
                div2.appendChild(img);
                var label = document.createElement("label");
                label.style.verticalAlign = "middle";
                var input = document.createElement("input");
                input.type = "checkbox";
                input.id = data[0]['name'];
                input.addEventListener("click", check_word_embedding_loaded);
                label.appendChild(input);
                var span = document.createElement("span");
                span.innerHTML += data[0]['name'] + ": n_words=" + data[0]['num_words'] + ", vec_size=" + data[0]['vector_size'];
                label.appendChild(span);
                div2.appendChild(label);
                word_embeddings_loaded.appendChild(div2);
                add_option_we_selections(data[0]['name'], data[0]['num_words'], data[0]['vector_size']);

                var data0 = data.shift();

                create_visualization(data, data0['name'], 'soft');

                loading.style.visibility = 'hidden';
            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error soft debiasing.")
            },
            contentType: "application/json",
            dataType: 'json'
        });

    //ATTRACT-REPEL
    } else if (select_debiasing.value == 'attract') {
        message['female_words'] = document.getElementById('female_words').value;
        message['male_words'] = document.getElementById('male_words').value;
        message['stereotypically_male_words'] = document.getElementById('stereotypically_male_words').value;
        message['stereotypically_female_words'] = document.getElementById('stereotypically_female_words').value;
        message['iterations'] = document.getElementById('iterations').value;
        message['batch_size'] = document.getElementById('batch_size').value;
        message['attr_margin'] = document.getElementById('attr_margin').value;
        message['rep_margin'] = document.getElementById('rep_margin').value;
        message['l2_reg_constant'] = document.getElementById('l2_reg_constant').value;


        $.ajax({
            type: 'POST',
            url: '/attract',
            data: JSON.stringify(message),
            success: function (data) {
                console.log(data);
                wordEmbeddings.push(data[0]);
                var div2 = document.createElement("div");
                div2.className = "cat action";
                var img = document.createElement("img");
                img.className = "sb-nav-link-icon";
                img.src = "static/assets/embed.png";
                img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
                div2.appendChild(img);
                var label = document.createElement("label");
                label.style.verticalAlign = "middle";
                var input = document.createElement("input");
                input.type = "checkbox";
                input.id = data[0]['name'];
                input.addEventListener("click", check_word_embedding_loaded);
                label.appendChild(input);
                var span = document.createElement("span");
                span.innerHTML += data[0]['name'] + ": n_words=" + data[0]['num_words'] + ", vec_size=" + data[0]['vector_size'];
                label.appendChild(span);
                div2.appendChild(label);
                word_embeddings_loaded.appendChild(div2);
                add_option_we_selections(data[0]['name'], data[0]['num_words'], data[0]['vector_size']);

                var data0 = data.shift();

                create_visualization(data, data0['name'], 'attract');

                loading.style.visibility = 'hidden';
            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error attract-repel debiasing.")
            },
            contentType: "application/json",
            dataType: 'json'
        });


    //LINEAR
    } else if (select_debiasing.value == 'linear') {
        message['visualize_words'] = document.getElementById('visualize_words').value;

        if (select_direction.value == 'pca') {
            message['gender_direction'] = 'pca';
            message['pairs'] = document.getElementById('pairs').value;

        } else if (select_direction.value == 'two_means') {
            message['gender_direction'] = 'two_means';
            message['female_words_direction'] = document.getElementById('female_words_direction').value;
            message['male_words_direction'] = document.getElementById('male_words_direction').value;
        }

        $.ajax({
            type: 'POST',
            url: '/linear',
            data: JSON.stringify(message),
            success: function (data) {
                console.log(data)
                wordEmbeddings.push(data[0]);
                var div2 = document.createElement("div");
                div2.className = "cat action";
                var img = document.createElement("img");
                img.className = "sb-nav-link-icon";
                img.src = "static/assets/embed.png";
                img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
                div2.appendChild(img);
                var label = document.createElement("label");
                label.style.verticalAlign = "middle";
                var input = document.createElement("input");
                input.type = "checkbox";
                input.id = data[0]['name'];
                input.addEventListener("click", check_word_embedding_loaded);
                label.appendChild(input);
                var span = document.createElement("span");
                span.innerHTML += data[0]['name'] + ": n_words=" + data[0]['num_words'] + ", vec_size=" + data[0]['vector_size'];
                label.appendChild(span);
                div2.appendChild(label);
                word_embeddings_loaded.appendChild(div2);
                add_option_we_selections(data[0]['name'], data[0]['num_words'], data[0]['vector_size']);

                var data0 = data.shift();

                create_visualization(data, data0['name'], 'linear');

                loading.style.visibility = 'hidden';
            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error linear projection debiasing.")
            },
            contentType: "application/json",
            dataType: 'json'
        });


    //DOUBLE HARD DEBIASING
    } else if (select_debiasing.value == 'double') {
        message['female_words'] = document.getElementById('female_words').value;
        message['male_words'] = document.getElementById('male_words').value;
        message['gender_neutral_words'] = document.getElementById('gender_neutral_words').value;
        if (select_direction.value == 'pca') {
            message['gender_direction'] = 'pca';
            message['pairs'] = document.getElementById('pairs').value;

        } else if (select_direction.value == 'two_means') {
            message['gender_direction'] = 'two_means';
            message['female_words_direction'] = document.getElementById('female_words_direction').value;
            message['male_words_direction'] = document.getElementById('male_words_direction').value;
        }

        $.ajax({
            type: 'POST',
            url: '/double',
            data: JSON.stringify(message),
            success: function (data) {
                console.log(data);
                wordEmbeddings.push(data[0]);
                var div2 = document.createElement("div");
                div2.className = "cat action";
                var img = document.createElement("img");
                img.className = "sb-nav-link-icon";
                img.src = "static/assets/embed.png";
                img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
                div2.appendChild(img);
                var label = document.createElement("label");
                label.style.verticalAlign = "middle";
                var input = document.createElement("input");
                input.type = "checkbox";
                input.id = data[0]['name'];
                input.addEventListener("click", check_word_embedding_loaded);
                label.appendChild(input);
                var span = document.createElement("span");
                span.innerHTML += data[0]['name'] + ": n_words=" + data[0]['num_words'] + ", vec_size=" + data[0]['vector_size'];
                label.appendChild(span);
                div2.appendChild(label);
                word_embeddings_loaded.appendChild(div2);
                add_option_we_selections(data[0]['name'], data[0]['num_words'], data[0]['vector_size']);

                var data0 = data.shift();

                create_visualization(data, data0['name'], 'double');

                loading.style.visibility = 'hidden';
            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error double-hard debiasing.")
            },
            contentType: "application/json",
            dataType: 'json'
        });


    //NULSPACE
    } else if (select_debiasing.value == 'nullspace') {
        message['female_words'] = document.getElementById('female_words').value;
        message['male_words'] = document.getElementById('male_words').value;
        message['neutral_words'] = document.getElementById('neutral_words').value;
        message['iterations'] = document.getElementById('iterations').value;


        $.ajax({
            type: 'POST',
            url: '/nullspace',
            data: JSON.stringify(message),
            success: function (data) {
                console.log(data);
                wordEmbeddings.push(data[0]);
                var div2 = document.createElement("div");
                div2.className = "cat action";
                var img = document.createElement("img");
                img.className = "sb-nav-link-icon";
                img.src = "static/assets/embed.png";
                img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
                div2.appendChild(img);
                var label = document.createElement("label");
                label.style.verticalAlign = "middle";
                var input = document.createElement("input");
                input.type = "checkbox";
                input.id = data[0]['name'];
                input.addEventListener("click", check_word_embedding_loaded);
                label.appendChild(input);
                var span = document.createElement("span");
                span.innerHTML += data[0]['name'] + ": n_words=" + data[0]['num_words'] + ", vec_size=" + data[0]['vector_size'];
                label.appendChild(span);
                div2.appendChild(label);
                word_embeddings_loaded.appendChild(div2);
                add_option_we_selections(data[0]['name'], data[0]['num_words'], data[0]['vector_size']);

                var data0 = data.shift();

                create_visualization(data, data0['name'], 'nullspace');

                loading.style.visibility = 'hidden';
            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error iterative nullspace projection.")
            },
            contentType: "application/json",
            dataType: 'json'
        });

    }

}

button_debiasing_options.addEventListener("click", click_button_debiasing_options);

//Change selected option on word embedding selection (Debiasing)
const change_select_we = (event) => {

    if (event.target.value == "") {
        select_debiasing.value = "";
        select_debiasing.disabled = true;
        select_direction.value = "";
        select_direction.disabled = true;
        while (div_debiasing_options.firstChild) {
            div_debiasing_options.removeChild(div_debiasing_options.firstChild);
        }
        button_debiasing_options.disabled = true;
    } else if (select_debiasing.disabled == true) {
        select_debiasing.disabled = false;
    }
}



//Change selected option on debiasing method (Debiasing)
const change_select_debiasing = (event) => {
    //hard, soft, attract, linear, double, nullspace
    while (div_debiasing_options.firstChild) {
        div_debiasing_options.removeChild(div_debiasing_options.firstChild);
    }
    button_debiasing_options.disabled = true;
    select_direction.value = "";
    if (event.target.value == "") {
        select_direction.disabled = true;
    } else {
        if (select_direction.disabled == true) {
            select_direction.disabled = false;
        }

        if (event.target.value == 'hard') {
            //gender_specific_words (pairs as "male,female;he,she"), gender_neutral_words, gender_direction
            for (let i = 0; i < select_direction.length; i++) {
                if (select_direction[i].value == "classification") {
                    if (select_direction[i].disabled == false) {
                        select_direction[i].disabled = true;
                    }
                } else {
                    select_direction[i].disabled = false;
                }
            }

        } else if (event.target.value == 'soft') {
            //gender_specific_words(he, she, male, female; no neutrals), gender_direction -- landa=0.2, epochs=100, lr=0.001, momentum=0.0
            //to visualize after debiasing add some neutral_words, but the method uses all word except neutral_words
            for (let i = 0; i < select_direction.length; i++) {
                if (select_direction[i].value == "classification") {
                    if (select_direction[i].disabled == false) {
                        select_direction[i].disabled = true;
                    }
                } else {
                    select_direction[i].disabled = false;
                }
            }

        } else if (event.target.value == 'attract') {
            //female_words, stereotypically_female_words, male_words, stereotypically_male_words -- iterations=5, batch_size=10. attr_margin=0.6, rep_margin=0.0, l2_reg_constant=0.000000001
            select_direction.value = "";
            select_direction.disabled = true;
            button_debiasing_options.disabled = false;
            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Female Words: ";
            var input = document.createElement("input");
            input.id = "female_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "female, woman, girl, sister, she, her, hers, daughter";
            div.appendChild(input);
            div.innerHTML += "Male Words: ";
            var input = document.createElement("input");
            input.id = "male_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "male, man, boy, brother, he, him, his, son";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Stereotypically Female Words: ";
            var input = document.createElement("input");
            input.id = "stereotypically_female_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "home, parents, children, family, cousins, marriage, wedding, relatives";
            div.appendChild(input);
            div.innerHTML += "Stereotypically Male Words: ";
            var input = document.createElement("input");
            input.id = "stereotypically_male_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "executive, management, professional, corporation, salary, office, business, career";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML += "Iterations: ";
            var input = document.createElement("input");
            input.id = "iterations";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "5";
            div.appendChild(input);
            div.innerHTML += "Batch size: ";
            var input = document.createElement("input");
            input.id = "batch_size";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "10";
            div.appendChild(input);
            div.innerHTML += "Attract margin: ";
            var input = document.createElement("input");
            input.id = "attr_margin";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "0.6";
            div.appendChild(input);
            div.innerHTML += "Repel margin: ";
            var input = document.createElement("input");
            input.id = "rep_margin";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "0.0";
            div.appendChild(input);
            div.innerHTML += "L2 Reg constant: ";
            var input = document.createElement("input");
            input.id = "l2_reg_constant";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 90px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "0.000000001";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

        } else if (event.target.value == 'linear') {
            //gender_direction
            //the method uses all words, so add some words to visualize
            for (let i = 0; i < select_direction.length; i++) {
                if (select_direction[i].value == "classification") {
                    if (select_direction[i].disabled == false) {
                        select_direction[i].disabled = true;
                    }
                } else {
                    select_direction[i].disabled = false;
                }
            }

        } else if (event.target.value == 'double') {
            //female_words, male_words, (gender_pairs or female_words_direction, male_words_direction)
            for (let i = 0; i < select_direction.length; i++) {
                if (select_direction[i].value == "classification") {
                    if (select_direction[i].disabled == false) {
                        select_direction[i].disabled = true;
                    }
                } else {
                    select_direction[i].disabled = false;
                }
            }

        } else if (event.target.value == 'nullspace') {
            //female_words, male_words, neutral_words, num_iter=35
            for (let i = 0; i < select_direction.length; i++) {
                if (select_direction[i].value == "pca" || select_direction[i].value == "two_means") {
                    if (select_direction[i].disabled == false) {
                        select_direction[i].disabled = true;
                    }
                } else {
                    select_direction[i].disabled = false;
                }
            }
        }
    }
}



//Change selected option on gender direction method (Debiasing)
const change_select_direction = (event) => {
    while (div_debiasing_options.firstChild) {
        div_debiasing_options.removeChild(div_debiasing_options.firstChild);
    }
    //pca, two_means, classification
    if (event.target.value == 'pca') {
        button_debiasing_options.disabled = false;
        if (select_debiasing.value == 'hard') {
            //gender_specific_words (pairs as "male,female;he,she"), gender_neutral_words, gender_direction
            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Gender Specific Words: ";
            var input = document.createElement("input");
            input.id = "gender_specific_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "husband, wife; brother, sister; dad, mom; actor, actress; boyfriend, girlfriend; king, queen";
            div.appendChild(input);
            div.innerHTML += "Gender Neutral Words: ";
            var input = document.createElement("input");
            input.id = "gender_neutral_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "math, algebra, geometry, calculus, equations, computation, numbers, addition, poetry, art, dance, literature, novel, symphony, drama, sculpture";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Pairs of Gender Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "pairs";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "woman, man; girl, boy; she, he; mother, father; daughter, son; gal, guy; female, male; her, his; herself, himself; mary, john";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

        } else if (select_debiasing.value == 'soft') {
            //gender_specific_words(he, she, male, female; no neutrals), gender_direction -- landa=0.2, epochs=100, lr=0.001, momentum=0.0
            //to visualize after debiasing add some neutral_words, but the method uses all word except neutral_words

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML += "Female Words: ";
            var input = document.createElement("input");
            input.id = "female_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "female, sister, hers, woman, girl, she, mother, daughter, gal, female, her, herself";
            div.appendChild(input);
            div.innerHTML += "Male Words: ";
            var input = document.createElement("input");
            input.id = "male_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "man, boy, he, father, son, guy, male, his, himself, father, brother, him";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML += "Gender Neutral Words: ";
            var input = document.createElement("input");
            input.id = "gender_neutral_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "math, algebra, geometry, calculus, equations, computation, numbers, addition, poetry, art, dance, literature, novel, symphony, drama, sculpture";
            div.appendChild(input);
            div.innerHTML += "Lambda: ";
            var input = document.createElement("input");
            input.id = "landa";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "0.2";
            div.appendChild(input);
            div.innerHTML += "Epochs: ";
            var input = document.createElement("input");
            input.id = "epochs";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "100";
            div.appendChild(input);
            div.innerHTML += "Learning rate: ";
            var input = document.createElement("input");
            input.id = "lr";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "0.001";
            div.appendChild(input);
            div.innerHTML += "Momentum: ";
            var input = document.createElement("input");
            input.id = "momentum";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "0.0";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Pairs of Gender Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "pairs";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "woman, man; girl, boy; she, he; mother, father; daughter, son; gal, guy; female, male; her, his; herself, himself; mary, john";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);


            

        } else if (select_debiasing.value == 'linear') {
            //gender_direction
            //the method uses all words, so add some words to visualize
            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Some words to visualize: ";
            var input = document.createElement("input");
            input.id = "visualize_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "math, geometry, computation, poetry, art, dance, literature, drama";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML += "Pairs of Gender Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "pairs";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "woman, man; girl, boy; she, he; mother, father; daughter, son; gal, guy; female, male; her, his; herself, himself; mary, john";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

        } else if (select_debiasing.value = 'double') {
            //female_words, male_words, (gender_pairs or female_words_direction, male_words_direction)
            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Stereotypically Female Words: ";
            var input = document.createElement("input");
            input.id = "female_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "caretaker, dancer, homemaker, librarian, nurse, secretary, hairdresser, housekeeper";
            div.appendChild(input);
            div.innerHTML += "Stereotypically Male Words: ";
            var input = document.createElement("input");
            input.id = "male_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "warrior, president, boxer, bodyguard, officer, mathematician, astronaut, coach";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML += "Gender Neutral Words: ";
            var input = document.createElement("input");
            input.id = "gender_neutral_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "math, algebra, geometry, calculus, equations, computation, numbers, addition, poetry, art, dance, literature, novel, symphony, drama, sculpture";
            div.appendChild(input);
            div.innerHTML += "Pairs of Gender Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "pairs";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "woman, man; girl, boy; she, he; mother, father; daughter, son; gal, guy; female, male; her, his; herself, himself; mary, john";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);
        }

    } else if (event.target.value == 'two_means') {
        button_debiasing_options.disabled = false;

        if (select_debiasing.value == 'hard') {
            //gender_specific_words (pairs as "male,female;he,she"), gender_neutral_words, gender_direction
            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Gender Specific Words: ";
            var input = document.createElement("input");
            input.id = "gender_specific_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "husband, wife; brother, sister; dad, mom; actor, actress; boyfriend, girlfriend; king, queen";
            div.appendChild(input);
            div.innerHTML += "Gender Neutral Words: ";
            var input = document.createElement("input");
            input.id = "gender_neutral_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "math, algebra, geometry, calculus, equations, computation, numbers, addition, poetry, art, dance, literature, novel, symphony, drama, sculpture";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Female Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "female_words_direction";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "woman, girl, she, mother, daughter, gal, female, her, herself, mary";
            div.appendChild(input);
            div.innerHTML += "Male Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "male_words_direction";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "man, boy, he, father, son, guy, male, his, himself, john";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

        } else if (select_debiasing.value == 'soft') {
            //gender_specific_words(he, she, male, female; no neutrals), gender_direction -- landa=0.2, epochs=100, lr=0.001, momentum=0.0
            //to visualize after debiasing add some neutral_words, but the method uses all word except neutral_words

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML += "Female Words: ";
            var input = document.createElement("input");
            input.id = "female_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "female, sister, hers, woman, girl, she, mother, daughter, gal, female, her, herself";
            div.appendChild(input);
            div.innerHTML += "Male Words: ";
            var input = document.createElement("input");
            input.id = "male_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "man, boy, he, father, son, guy, male, his, himself, father, brother, him";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML += "Gender Neutral Words: ";
            var input = document.createElement("input");
            input.id = "gender_neutral_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "math, algebra, geometry, calculus, equations, computation, numbers, addition, poetry, art, dance, literature, novel, symphony, drama, sculpture";
            div.appendChild(input);
            div.innerHTML += "Lambda: ";
            var input = document.createElement("input");
            input.id = "landa";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "0.2";
            div.appendChild(input);
            div.innerHTML += "Epochs: ";
            var input = document.createElement("input");
            input.id = "epochs";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "100";
            div.appendChild(input);
            div.innerHTML += "Learning rate: ";
            var input = document.createElement("input");
            input.id = "lr";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "0.001";
            div.appendChild(input);
            div.innerHTML += "Momentum: ";
            var input = document.createElement("input");
            input.id = "momentum";
            input.type = "number";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "0.0";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Female Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "female_words_direction";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "woman, girl, she, mother, daughter, gal, female, her, herself, mary";
            div.appendChild(input);
            div.innerHTML += "Male Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "male_words_direction";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "man, boy, he, father, son, guy, male, his, himself, john";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

        } else if (select_debiasing.value == 'linear') {
            //gender_direction
            //the method uses all words, so add some words to visualize
            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Some words to visualize: ";
            var input = document.createElement("input");
            input.id = "visualize_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "math, geometry, computation, poetry, art, dance, literature, drama";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML += "Female Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "female_words_direction";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "woman, girl, she, mother, daughter, gal, female, her, herself, mary";
            div.appendChild(input);
            div.innerHTML += "Male Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "male_words_direction";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "man, boy, he, father, son, guy, male, his, himself, john";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

        } else if (select_debiasing.value = 'double') {
            //female_words, male_words, (gender_pairs or female_words_direction, male_words_direction)
            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Stereotypically Female Words: ";
            var input = document.createElement("input");
            input.id = "female_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "caretaker, dancer, homemaker, librarian, nurse, secretary, hairdresser, housekeeper";
            div.appendChild(input);
            div.innerHTML += "Stereotypically Male Words: ";
            var input = document.createElement("input");
            input.id = "male_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "warrior, president, boxer, bodyguard, officer, mathematician, astronaut, coach";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML += "Gender Neutral Words: ";
            var input = document.createElement("input");
            input.id = "gender_neutral_words";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "math, algebra, geometry, calculus, equations, computation, numbers, addition, poetry, art, dance, literature, novel, symphony, drama, sculpture";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

            var div = document.createElement("div");
            div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
            div.innerHTML = "Female Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "female_words_direction";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "woman, girl, she, mother, daughter, gal, female, her, herself, mary";
            div.appendChild(input);
            div.innerHTML += "Male Words (gender direction): ";
            var input = document.createElement("input");
            input.id = "male_words_direction";
            input.type = "text";
            input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
            input.defaultValue = "man, boy, he, father, son, guy, male, his, himself, john";
            div.appendChild(input);
            div_debiasing_options.appendChild(div);

        }

    } else if (event.target.value == 'classification') {
        button_debiasing_options.disabled = false;
        var div = document.createElement("div");
        div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
        div.innerHTML = "Stereotypically Female Words: ";
        var input = document.createElement("input");
        input.id = "female_words";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "caretaker, dancer, homemaker, librarian, nurse, secretary, hairdresser, housekeeper";
        div.appendChild(input);
        div.innerHTML += "Stereotypically Male Words: ";
        var input = document.createElement("input");
        input.id = "male_words";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "warrior, president, boxer, bodyguard, officer, mathematician, astronaut, coach";
        div.appendChild(input);
        div_debiasing_options.appendChild(div);

        var div = document.createElement("div");
        div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
        div.innerHTML = "Neutral Words: ";
        var input = document.createElement("input");
        input.id = "neutral_words";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "home, parents, children, family, cousins, marriage, wedding, relatives, executive, management, professional, corporation, salary, office, business, career";
        div.appendChild(input);
        div.innerHTML += "Iterations: ";
        var input = document.createElement("input");
        input.id = "iterations";
        input.type = "number";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "35";
        div.appendChild(input);
        div_debiasing_options.appendChild(div);

    } else if (event.target.value == "") {
        button_debiasing_options.disabled = true;
    }
}


select_we.addEventListener("change", change_select_we);
select_debiasing.addEventListener("change", change_select_debiasing);
select_direction.addEventListener("change", change_select_direction);





//Change selected option on word embedding 1 (Measurement)
const change_select_we_1 = (event) => {
    if (select_we_1.value != "" && select_measurement_method.value != "" || select_we_2.value != "" && select_measurement_method.value != "") {
        if (select_measurement_method.value == 'weat' || select_measurement_method.value == 'neighborhood' || ((select_measurement_method.value == 'direct' || select_measurement_method.value == 'indirect') && document.getElementById('gender_direction_method_measurements').value != "")) {
            if (button_measurements.disabled == true) {
                button_measurements.disabled = false;
            }
        } else if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }
    } else if (button_measurements.disabled == false) {
        button_measurements.disabled = true;
    }
}



//Change selected option on word embedding 2 (Measurement)
const change_select_we_2 = (event) => {
    if (select_we_1.value != "" && select_measurement_method.value != "" || select_we_2.value != "" && select_measurement_method.value != "") {
        if (select_measurement_method.value == 'weat' || select_measurement_method.value == 'neighborhood' || ((select_measurement_method.value == 'direct' || select_measurement_method.value == 'indirect') && document.getElementById('gender_direction_method_measurements').value != "")) {
            if (button_measurements.disabled == true) {
                button_measurements.disabled = false;
            }
        } else if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }
    } else if (button_measurements.disabled == false) {
        button_measurements.disabled = true;
    }
}



//Change selected option on measurement method (Measurement)
const change_select_measurement_method = (event) => {
    //direct, indirect, weat, neighborhood 
    while (div_measurements_options.firstChild) {
        div_measurements_options.removeChild(div_measurements_options.firstChild);
    }
    if (event.target.value == "indirect") {
        var div = document.createElement("div");
        div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
        div.innerHTML = "First word: ";
        var input = document.createElement("input");
        input.id = "w";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 100px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "softball";
        div.appendChild(input);
        div.innerHTML += "Second word: ";
        var input = document.createElement("input");
        input.id = "v";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 100px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "receptionist";
        div.appendChild(input);
        div.innerHTML += 'Select Gender Direction Method:';
        var select = document.createElement("select");
        select.id = "gender_direction_method_measurements";
        select.class = "select";
        select.style.cssText = "padding-top: 1.25px; padding-bottom:1.25px;margin-left: 5px; margin-right: 20px; width: 150px; background-color: rgba(13, 110, 253, 0.5); font-family: var(--bs-body-font-family); border: none;";
        var option = document.createElement("option");
        option.value = "";
        option.innerHTML = "-- Select method --";
        select.appendChild(option);
        var option = document.createElement("option");
        option.value = "pca";
        option.innerHTML = "PCA Pairs";
        select.appendChild(option);
        var option = document.createElement("option");
        option.value = "two_means";
        option.innerHTML = "Two Means";
        select.appendChild(option);
        select.addEventListener("change", gender_direction_method_change);
        div.append(select);
        div_measurements_options.appendChild(div);
        if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }

    } else if (event.target.value == "direct") {

        var div = document.createElement("div");
        div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
        div.innerHTML = "Gender Neutral Words: ";
        var input = document.createElement("input");
        input.id = "gender_neutral_words_measurements";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "home, parents, children, family, cousins, marriage, wedding, relatives, executive, management, professional, corporation, salary, office, business, career";
        div.appendChild(input);
        div.innerHTML += "c: ";
        var input = document.createElement("input");
        input.id = "c";
        input.type = "number";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 50px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "1";
        div.appendChild(input);
        div.innerHTML += 'Select Gender Direction Method:';
        var select = document.createElement("select");
        select.id = "gender_direction_method_measurements";
        select.class = "select";
        select.style.cssText = "padding-top: 1.25px; padding-bottom:1.25px;margin-left: 5px; margin-right: 20px; width: 150px; background-color: rgba(13, 110, 253, 0.5); font-family: var(--bs-body-font-family); border: none; ";
        var option = document.createElement("option");
        option.value = "";
        option.innerHTML = "-- Select method --";
        select.appendChild(option);
        var option = document.createElement("option");
        option.value = "pca";
        option.innerHTML = "PCA Pairs";
        select.appendChild(option);
        var option = document.createElement("option");
        option.value = "two_means";
        option.innerHTML = "Two Means";
        select.appendChild(option);
        select.addEventListener("change", gender_direction_method_change);
        div.append(select);
        div_measurements_options.appendChild(div);
        if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }

    } else if (event.target.value == "weat") {

        var div = document.createElement("div");
        div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
        div.innerHTML = "Target words X (stereotypically female): ";
        var input = document.createElement("input");
        input.id = "tarjet_words_x";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "caretaker, dancer, homemaker, librarian, nurse, secretary, hairdresser, housekeeper";
        div.appendChild(input);
        div.innerHTML += "Target Words Y (stereotypically male): ";
        var input = document.createElement("input");
        input.id = "tarjet_words_y";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "warrior, president, boxer, bodyguard, officer, mathematician, astronaut, coach";
        div.appendChild(input);
        div_measurements_options.appendChild(div);

        var div = document.createElement("div");
        div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
        div.innerHTML = "Attribute Words A (female): ";
        var input = document.createElement("input");
        input.id = "attr_words_a";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "woman, girl, she, mother, daughter, gal, female, her, herself, mary";
        div.appendChild(input);
        div.innerHTML += "Attribute Words B (male): ";
        var input = document.createElement("input");
        input.id = "attr_words_b";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "man, boy, he, father, son, guy, male, his, himself, john";
        div.appendChild(input);
        div_measurements_options.appendChild(div);
        if (select_we_1.value != "" || select_we_2.value != "") {
            if (button_measurements.disabled == true) {
                button_measurements.disabled = false;
            }
        } else if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }
    } else if (event.target.value == "neighborhood") {
        var div = document.createElement("div");
        div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
        div.innerHTML = "Stereotipically Female Words: ";
        var input = document.createElement("input");
        input.id = "female_words_measurements";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "caretaker, dancer, homemaker, librarian, nurse, secretary, hairdresser, housekeeper";
        div.appendChild(input);
        div.innerHTML += "Stereotipically Male Words: ";
        var input = document.createElement("input");
        input.id = "male_words_measurements";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "warrior, president, boxer, bodyguard, officer, mathematician, astronaut, coach";
        div.appendChild(input);
        div_measurements_options.appendChild(div);
        if (select_we_1.value != "" || select_we_2.value != "") {
            if (button_measurements.disabled == true) {
                button_measurements.disabled = false;
            }
        } else if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }
    } else {
        if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }
    }

}


//Click button measure in Measurements
const click_button_measurements = (event) => {
    if (select_measurement_method.value == "indirect") {
        loading.style.visibility = 'visible';

        var message = {};
        message['w'] = document.getElementById('w').value;
        message['v'] = document.getElementById('v').value;
        
        if (document.getElementById('gender_direction_method_measurements').value == 'pca') {
            message['gender_direction'] = 'pca';
            message['pairs'] = document.getElementById("pairs_measurements").value;

            if (select_we_1.value != '' && select_we_2.value != '') {
                message['name_1'] = select_we_1.value;
                message['name_2'] = select_we_2.value;
               
            } else if (select_we_1.value != '') {
                message['name_1'] = select_we_1.value;

            } else if (select_we_2.value != '') {
                message['name_2'] = select_we_2.value;
            }

        } else if (document.getElementById('gender_direction_method_measurements').value == 'two_means') {
            message['gender_direction'] = 'two_means';
            message['female_words_direction'] = document.getElementById("female_words_direction_measurements").value;
            message['male_words_direction'] = document.getElementById("male_words_direction_measurements").value;

            if (select_we_1.value != '' && select_we_2.value != '') {
                message['name_1'] = select_we_1.value;
                message['name_2'] = select_we_2.value;

            } else if (select_we_1.value != '') {
                message['name_1'] = select_we_1.value;

            } else if (select_we_2.value != '') {
                message['name_2'] = select_we_2.value;
            }
        }
        $.ajax({
            type: 'POST',
            url: '/indirect',
            data: JSON.stringify(message),
            success: function (data) {
                var newData;

                if ('indirect_bias1' in data && 'indirect_bias2' in data) {
                    newData = [
                        {
                            "Method": "Indirect Bias",
                            "Word Embedding 1": message['name_1'] + ": (" + message['w'] + '/' + message['v'] + ")= " + data['indirect_bias1'],
                            "Word Embedding 2": message['name_2'] + ": (" + message['w'] + '/' + message['v'] + ")= " + data['indirect_bias2'],
                        }
                    ];

                } else if ('indirect_bias1' in data) {
                    newData = [
                        {
                            "Method": "Indirect Bias",
                            "Word Embedding 1": message['name_1'] + ": (" + message['w'] + '/' + message['v'] + ")= " + data['indirect_bias1'],
                            "Word Embedding 2": "",
                        }
                    ];

                } else if ('indirect_bias2' in data) {
                    newData = [
                        {
                            "Method": "Indirect Bias",
                            "Word Embedding 1": "",
                            "Word Embedding 2": message['name_2'] + ": (" + message['w'] + '/' + message['v'] + ")= " + data['indirect_bias2'],
                        }
                    ];
                }


                dataTable.insert(newData);
                loading.style.visibility = 'hidden';
            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error in Indirect Bias.")
            },
            contentType: "application/json",
            dataType: 'json'
        });
    } else if (select_measurement_method.value == "direct") {
        loading.style.visibility = 'visible';
        var message = {};
        message['gender_neutral_words'] = document.getElementById('gender_neutral_words_measurements').value;
        message['c'] = document.getElementById('c').value;

        if (document.getElementById('gender_direction_method_measurements').value == 'pca') {
            message['gender_direction'] = 'pca';
            message['pairs'] = document.getElementById("pairs_measurements").value;

            if (select_we_1.value != '' && select_we_2.value != '') {
                message['name_1'] = select_we_1.value;
                message['name_2'] = select_we_2.value;

            } else if (select_we_1.value != '') {
                message['name_1'] = select_we_1.value;

            } else if (select_we_2.value != '') {
                message['name_2'] = select_we_2.value;
            }

        } else if (document.getElementById('gender_direction_method_measurements').value == 'two_means') {
            message['gender_direction'] = 'two_means';
            message['female_words_direction'] = document.getElementById("female_words_direction_measurements").value;
            message['male_words_direction'] = document.getElementById("male_words_direction_measurements").value;

            if (select_we_1.value != '' && select_we_2.value != '') {
                message['name_1'] = select_we_1.value;
                message['name_2'] = select_we_2.value;

            } else if (select_we_1.value != '') {
                message['name_1'] = select_we_1.value;

            } else if (select_we_2.value != '') {
                message['name_2'] = select_we_2.value;
            }
        }
        $.ajax({
            type: 'POST',
            url: '/direct',
            data: JSON.stringify(message),
            success: function (data) {
                var newData;

                if ('direct_bias1' in data && 'direct_bias2' in data) {
                    newData = [
                        {
                            "Method": "Direct Bias",
                            "Word Embedding 1": message['name_1'] + ": " + data['direct_bias1'],
                            "Word Embedding 2": message['name_2'] + ": " + data['direct_bias2'],
                        }
                    ];

                } else if ('direct_bias1' in data) {
                    newData = [
                        {
                            "Method": "Direct Bias",
                            "Word Embedding 1": message['name_1'] + ": " + data['direct_bias1'],
                            "Word Embedding 2": "",
                        }
                    ];

                } else if ('direct_bias2' in data) {
                    newData = [
                        {
                            "Method": "Direct Bias",
                            "Word Embedding 1": "",
                            "Word Embedding 2": message['name_2'] + ": " + data['direct_bias2'],
                        }
                    ];
                }


                dataTable.insert(newData);
                loading.style.visibility = 'hidden';
            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error in Direct Bias.")
            },
            contentType: "application/json",
            dataType: 'json'
        });
    } else if (select_measurement_method.value == "weat") {
        loading.style.visibility = 'visible';

        var message = {};
        message['tarjet_words_x'] = document.getElementById('tarjet_words_x').value;
        message['tarjet_words_y'] = document.getElementById('tarjet_words_y').value;     
        message['attr_words_a'] = document.getElementById('attr_words_a').value;
        message['attr_words_b'] = document.getElementById('attr_words_b').value;

        if (select_we_1.value != '' && select_we_2.value != '') {
            message['name_1'] = select_we_1.value;
            message['name_2'] = select_we_2.value;

        } else if (select_we_1.value != '') {
            message['name_1'] = select_we_1.value;

        } else if (select_we_2.value != '') {
            message['name_2'] = select_we_2.value;
        }

        $.ajax({
            type: 'POST',
            url: '/weat',
            data: JSON.stringify(message),
            success: function (data) {
                var newData;

                if ('effect_size1' in data && 'effect_size2' in data) {
                    newData = [
                        {
                            "Method": "WEAT",
                            "Word Embedding 1": message['name_1'] + ": effect size=" + data['effect_size1'] + ", p-value=" + data['p_value1'],
                            "Word Embedding 2": message['name_2'] + ": effect size=" + data['effect_size2'] + ", p-value=" + data['p_value2'],
                        }
                    ];

                } else if ('effect_size1' in data) {
                    newData = [
                        {
                            "Method": "WEAT",
                            "Word Embedding 1": message['name_1'] + ": effect size=" + data['effect_size1'] + ", p-value=" + data['p_value1'],
                            "Word Embedding 2": "",
                        }
                    ];

                } else if ('effect_size2' in data) {
                    newData = [
                        {
                            "Method": "WEAT",
                            "Word Embedding 1": "",
                            "Word Embedding 2": message['name_2'] + ": effect size=" + data['effect_size2'] + ", p-value=" + data['p_value2'],
                        }
                    ];
                }


                dataTable.insert(newData);
                loading.style.visibility = 'hidden';
            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error in WEAT.")
            },
            contentType: "application/json",
            dataType: 'json'
        });


    } else if (select_measurement_method.value == "neighborhood") {
        loading.style.visibility = 'visible';

        var message = {};
        message['female_words'] = document.getElementById('female_words_measurements').value;
        message['male_words'] = document.getElementById('male_words_measurements').value;

        if (select_we_1.value != '' && select_we_2.value != '') {
            message['name_1'] = select_we_1.value;
            message['name_2'] = select_we_2.value;

        } else if (select_we_1.value != '') {
            message['name_1'] = select_we_1.value;

        } else if (select_we_2.value != '') {
            message['name_2'] = select_we_2.value;
        }

        $.ajax({
            type: 'POST',
            url: '/neighborhood',
            data: JSON.stringify(message),
            success: function (data) {
                var newData;

                if ('neighborhood_metric1' in data && 'neighborhood_metric2' in data) {
                    newData = [
                        {
                            "Method": "Neighborhood Metric",
                            "Word Embedding 1": message['name_1'] + ": " + data['neighborhood_metric1'],
                            "Word Embedding 2": message['name_2'] + ": " + data['neighborhood_metric2'],
                        }
                    ];

                } else if ('neighborhood_metric1' in data) {
                    newData = [
                        {
                            "Method": "Neighborhood Metric",
                            "Word Embedding 1": message['name_1'] + ": " + data['neighborhood_metric1'],
                            "Word Embedding 2": "",
                        }
                    ];

                } else if ('neighborhood_metric2' in data) {
                    newData = [
                        {
                            "Method": "Neighborhood Metric",
                            "Word Embedding 1": "",
                            "Word Embedding 2": message['name_2'] + ": " + data['neighborhood_metric2'],
                        }
                    ];
                }
                

                dataTable.insert(newData);

                loading.style.visibility = 'hidden';
            },
            error: function (error) {
                console.log(error);
                loading.style.visibility = 'hidden';
                alert("Error in Neighborhood Metric.")
            },
            contentType: "application/json",
            dataType: 'json'
        });
    }
}


button_measurements.addEventListener("click", click_button_measurements);


//Change gender direction method of measurements when direct or indirect measurement are selected
const gender_direction_method_change = (event) => {
    if (div_measurements_options.childNodes.length == 2) {
        div_measurements_options.removeChild(div_measurements_options.lastChild);
    }
    if (event.target.value == 'pca') {
        var div = document.createElement("div");
        div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
        div.innerHTML += "Pairs of Gender Words (gender direction): ";
        var input = document.createElement("input");
        input.id = "pairs_measurements";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "woman, man; girl, boy; she, he; mother, father; daughter, son; gal, guy; female, male; her, his; herself, himself; mary, john";
        div.appendChild(input);
        div_measurements_options.appendChild(div);
        if (select_we_1.value != "" || select_we_2.value != "") {
            if (button_measurements.disabled == true) {
                button_measurements.disabled = false;
            }
        } else if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }
    } else if (event.target.value == 'two_means') {
        var div = document.createElement("div");
        div.style.cssText = "color: rgb(33 37 41);font-size: 13px;padding-bottom: 1rem;";
        div.innerHTML = "Female Words (gender direction): ";
        var input = document.createElement("input");
        input.id = "female_words_direction_measurements";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "woman, girl, she, mother, daughter, gal, female, her, herself, mary";
        div.appendChild(input);
        div.innerHTML += "Male Words (gender direction): ";
        var input = document.createElement("input");
        input.id = "male_words_direction_measurements";
        input.type = "text";
        input.style.cssText = "margin-left: 5px; margin-right: 20px; width: 500px; background-color: rgb(133 182 254); color: rgb(33 37 41); border: none;";
        input.defaultValue = "man, boy, he, father, son, guy, male, his, himself, john";
        div.appendChild(input);
        div_measurements_options.appendChild(div);
        if (select_we_1.value != "" || select_we_2.value != "") {
            if (button_measurements.disabled == true) {
                button_measurements.disabled = false;
            }
        } else if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }
    } else {
        if (button_measurements.disabled == false) {
            button_measurements.disabled = true;
        }
    }
}


select_we_1.addEventListener("change", change_select_we_1);
select_we_2.addEventListener("change", change_select_we_2);
select_measurement_method.addEventListener("change", change_select_measurement_method);



//Add new option of the new WE in select_we, select_we_1 and select_we_2 (and set enable select_measurement_method)
function add_option_we_selections(name, num_words, vec_size) {
    if (wordEmbeddings.length == 1) {
        select_we.disabled = false;
        select_we_1.disabled = false;
        select_we_2.disabled = false;
        select_measurement_method.disabled = false;
    }
    var option = document.createElement("option");
    option.value = name;
    option.innerHTML = name + ": w=" + num_words + ", s=" + vec_size;
    select_we.appendChild(option);
    var option = document.createElement("option");
    option.value = name;
    option.innerHTML = name + ": w=" + num_words + ", s=" + vec_size;
    select_we_1.appendChild(option);
    var option = document.createElement("option");
    option.value = name;
    option.innerHTML = name + ": w=" + num_words + ", s=" + vec_size;
    select_we_2.appendChild(option);
}

//Delete option of WE in select_we, select_we_1 and select_we_2 (and disable select_measurement_method, select_debiasing, select_direction)
function delete_option_we_selections(name) {
    if (wordEmbeddings.length == 1) {
        select_we.value = "";
        select_we_1.value = "";
        select_we_2.value = "";
        select_we.disabled = true;
        select_we_1.disabled = true;
        select_we_2.disabled = true;
        select_measurement_method.value = "";
        select_measurement_method.disabled = true;
        select_debiasing.value = "";
        select_debiasing.disabled = true;
        select_direction.value = "";
        select_direction.disabled = true;
    }

    var idx=-1;
    for (let i = 0; i < select_we.length; i++) {
        if (select_we[i].value == name) {
            idx=i;
            break;
        }
    }
    select_we.remove(idx);

    var idx = -1;
    for (let i = 0; i < select_we_1.length; i++) {
        if (select_we_1[i].value == name) {
            idx = i;
            break;
        }
    }
    select_we_1.remove(idx);

    var idx = -1;
    for (let i = 0; i < select_we_2.length; i++) {
        if (select_we_2[i].value == name) {
            idx = i;
            break;
        }
    }
    select_we_2.remove(idx);
}

//Save WE on file
const click_save_word_embedding = (event) => {
    event.preventDefault();
    loading.style.visibility = 'visible';
    var word_embedding_save = {};
    for (let i = 0; i < wordEmbeddings.length; i++) {
        if (document.getElementById(wordEmbeddings[i]['name']).checked == true) {
            word_embedding_save = { 'name': wordEmbeddings[i]['name'], 'vector_size': wordEmbeddings[i]['vector_size'], 'num_words': wordEmbeddings[i]['num_words'] };
            break;
        }
    }

    $.ajax({
        type: 'POST',
        url: '/save_we',
        data: JSON.stringify({
            'name': word_embedding_save['name'],
            'vector_size': word_embedding_save['vector_size'],
            'num_words': word_embedding_save['num_words']
        }),
        success: function (data) {
            console.log(data)
            document.getElementById(word_embedding_save['name']).checked = false;
            save_word_embedding_button.disabled = true;
            delete_word_embedding_button.disabled = true;
            loading.style.visibility = 'hidden';
        },
        error: function (error) {
            console.log(error);
            loading.style.visibility = 'hidden';
            alert("Error saving the word embedding.")
        },
        contentType: "application/json",
        dataType: 'json'
    });

};


//delete WE
const click_delete_word_embedding = (event) => {
    event.preventDefault();
    loading.style.visibility = 'visible';
    var word_embedding_del = {};
    var aux = 0;
    
    for (let i = 0; i < wordEmbeddings.length; i++) {
        if (document.getElementById(wordEmbeddings[i]['name']).checked == true) {
            console.log(wordEmbeddings[i]['name'])
            word_embedding_del = { 'name': wordEmbeddings[i]['name'], 'vector_size': wordEmbeddings[i]['vector_size'], 'num_words': wordEmbeddings[i]['num_words'] };
            aux = i;
            break;
        }
    }
    $.ajax({
        type: 'POST',
        url: '/delete_we',
        data: JSON.stringify({
            'name': word_embedding_del['name'],
            'vector_size': word_embedding_del['vector_size'],
            'num_words': word_embedding_del['num_words']
        }),
        success: function (data) {
            for (let i = 0; i < wordEmbeddings.length; i++) {
                document.getElementById(wordEmbeddings[i]['name']).removeEventListener("change", check_word_embedding_loaded);
            }
            delete_option_we_selections(wordEmbeddings[aux]['name']);
            wordEmbeddings.splice(aux, 1);
            while (word_embeddings_loaded.firstChild) {
                word_embeddings_loaded.removeChild(word_embeddings_loaded.firstChild);
            }
            for (let i = 0; i < wordEmbeddings.length; i++) {
                var div2 = document.createElement("div");
                div2.className = "cat action";
                var img = document.createElement("img");
                img.className = "sb-nav-link-icon";
                img.src = "static/assets/embed.png";
                img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
                div2.appendChild(img);
                var label = document.createElement("label");
                label.style.verticalAlign = "middle";
                var input = document.createElement("input");
                input.type = "checkbox";
                input.id = wordEmbeddings[i]['name'];
                input.addEventListener("click", check_word_embedding_loaded);
                label.appendChild(input);
                var span = document.createElement("span");
                span.innerHTML += wordEmbeddings[i]['name'] + ": n_words=" + wordEmbeddings[i]['num_words'] + ", vec_size=" + wordEmbeddings[i]['vector_size'];
                label.appendChild(span);
                div2.appendChild(label);
                word_embeddings_loaded.appendChild(div2);
            }
            save_word_embedding_button.disabled = true;
            delete_word_embedding_button.disabled = true;
            button_debiasing_options.disabled = true;
            button_measurements.disabled = true;
            while (div_debiasing_options.firstChild) {
                div_debiasing_options.removeChild(div_debiasing_options.firstChild);
            }
            while (div_measurements_options.firstChild) {
                div_measurements_options.removeChild(div_measurements_options.firstChild);
            }
            loading.style.visibility = 'hidden';

        },
        error: function (error) {
            console.log(error);
            loading.style.visibility = 'hidden';
            alert("Error deleting the word embedding.")
        },
        contentType: "application/json",
        dataType: 'json'
    });
};

save_word_embedding_button.addEventListener("click", click_save_word_embedding);
delete_word_embedding_button.addEventListener("click", click_delete_word_embedding);

const loading = document.getElementById("loading");



//Change selected option sidevar: upload WE from file or create/compute WE from corpus
const upload_change = (event) => {
    while (form_sidebar.firstChild) {
        form_sidebar.removeChild(form_sidebar.firstChild);
    }
    if (event.target.value == "we") {
        var div = document.createElement("div");
        div.className = "nav-link";
        div.innerHTML += 'Path Corpus file \'*.txt\'';
        var input = document.createElement("input");
        input.type = "text";
        input.id = "corpus_file";
        input.style.cssText = "width: 350px; font-size: 12px;";
        div.appendChild(input);
        form_sidebar.appendChild(div);
        var div = document.createElement("div");
        div.className = "nav-link";
        div.innerHTML += 'Select Word Embedding Type:';
        var select = document.createElement("select");
        select.id = "we_type";
        select.class = "select";
        select.style.cssText = "margin-top:-10px; background-color: #343a40; display: block; margin-left: 1rem; color: rgba(255, 255, 255, 0.5); font-family: var(--bs-body-font-family); border: none;";
        var option = document.createElement("option");
        option.value = "";
        option.innerHTML = "-- Select type --";
        select.appendChild(option);
        var option = document.createElement("option");
        option.value = "w2v";
        option.innerHTML = "Word2Vec";
        select.appendChild(option);
        var option = document.createElement("option");
        option.value = "glove";
        option.innerHTML = "Glove";
        select.appendChild(option);
        select.addEventListener("change", embedding_type_change);
        div.append(select);
        form_sidebar.appendChild(div);

    } else if (event.target.value == "upload") {
        var div = document.createElement("div");
        div.className = "nav-link";
        div.innerHTML += 'Path Word Embeddings file \'*.txt\'';
        var input = document.createElement("input");
        input.id = "we_file";
        input.type = "text";
        input.style.cssText = "width: 350px; font-size: 12px;";
        div.appendChild(input);
        form_sidebar.appendChild(div);
        var div = document.createElement("div");
        div.className = "nav-link";
        div.style.marginTop = "10px";
        var button = document.createElement("button");
        button.id = "upload_we_button";
        button.className = "button-4";
        button.role = "button";
        button.style.margin = "auto";
        button.innerHTML = "Upload";
        button.addEventListener("click", upload_click);
        div.appendChild(button);
        form_sidebar.appendChild(div);
    }
};

const form_sidebar = document.getElementById("form_sidebar");

const upload = document.getElementById("upload");
upload.addEventListener("change", upload_change);


//Click on upload button for upload word embedding with selected path
const upload_click = (event) => {
    event.preventDefault();
    var check_text = document.getElementById("we_file").value.slice(-".txt".length) != ".txt";
    if (check_text) {
        alert("Choose a file '.txt'")
        event.target.value = null;
        return;
    };
    loading.style.visibility = 'visible';

    $.ajax({
        type: 'POST',
        url: '/upload_we',
        data: JSON.stringify({ 'path': document.getElementById("we_file").value }),
        success: function (data) {
            wordEmbeddings.push(data);
            var div2 = document.createElement("div");
            div2.className = "cat action";
            var img = document.createElement("img");
            img.className = "sb-nav-link-icon";
            img.src = "static/assets/embed.png";
            img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
            div2.appendChild(img);
            var label = document.createElement("label");
            label.style.verticalAlign = "middle";
            var input = document.createElement("input");
            input.type = "checkbox";
            input.id = data['name'];
            input.addEventListener("click", check_word_embedding_loaded);
            label.appendChild(input);
            var span = document.createElement("span");
            span.innerHTML += data['name'] + ": n_words=" + data['num_words'] + ", vec_size=" + data['vector_size'];
            label.appendChild(span);
            div2.appendChild(label);
            word_embeddings_loaded.appendChild(div2);
            while (form_sidebar.firstChild) {
                form_sidebar.removeChild(form_sidebar.firstChild);
            }
            upload.value = "";
            add_option_we_selections(data['name'], data['num_words'], data['vector_size']);
            loading.style.visibility = 'hidden';
        },
        error: function (error) {
            console.log(error);
            loading.style.visibility = 'hidden';
            alert("Error uploading the word embedding file.")
        },
        contentType: "application/json",
        dataType: 'json'
    });
   

};


//Click on loaded list of Word embeddings on sidevar
const check_word_embedding_loaded = (event) => {
    if (event.target.checked == true) {
        save_word_embedding_button.disabled = false;
        delete_word_embedding_button.disabled = false;
        for (let i = 0; i < wordEmbeddings.length; i++) {
            let check = document.getElementById(wordEmbeddings[i]['name']);
            if (check.id != event.target.id && check.checked == true) {
                check.checked = false;
            }
        }
    } else {
        save_word_embedding_button.disabled = true;
        delete_word_embedding_button.disabled = true;
    }
};


////On selector's change show form for glove or w2v
const embedding_type_change = (event) => {
    while (form_sidebar.childNodes.length > 2) {
        form_sidebar.removeChild(form_sidebar.lastChild);
    }

    if (event.target.value == "w2v") {
        var div = document.createElement("div");
        div.className = "nav-link";
        div.innerHTML = "Insert parameters:";
        div.style.marginBottom = "-20px";
        form_sidebar.appendChild(div);
        var div = document.createElement("div");
        div.className = "nav-link";
        div.style.color = "#85b6fe";
        div.style.fontSize="13px";
        div.innerHTML += 'Vector size:';
        var input = document.createElement("input");
        input.id = "vector_size";
        input.min = "50";
        input.max = "300";
        input.defaultValue = "200";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        div.innerHTML += 'Window size:';
        var input = document.createElement("input");
        input.id = "window_size";
        input.min = "2";
        input.defaultValue = "10";
        input.max = "15";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        form_sidebar.appendChild(div);
        var div = document.createElement("div");
        div.style.fontSize = "13px";
        div.className = "nav-link";
        div.style.color = "#85b6fe";
        div.innerHTML += 'Min count:';
        var input = document.createElement("input");
        input.id = "min_count";
        input.min = "2";
        input.defaultValue = "2";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        form_sidebar.appendChild(div);
        var div = document.createElement("div");
        div.className = "nav-link";
        div.style.marginTop = "10px";
        var button = document.createElement("button");
        button.id = "compute_w2v_button";
        button.className = "button-4";
        button.role = "button";
        button.style.margin = "auto";
        button.innerHTML = "Compute";
        button.addEventListener("click", compute_w2v_click);
        div.appendChild(button);
        form_sidebar.appendChild(div);

    } else if (event.target.value == "glove") {

        var div = document.createElement("div");
        div.className = "nav-link";
        div.innerHTML = "Insert parameters:";
        div.style.marginBottom = "-20px";
        form_sidebar.appendChild(div);
        var div = document.createElement("div");
        div.className = "nav-link";
        div.style.color = "#85b6fe";
        div.style.fontSize = "13px";
        div.innerHTML += 'Vector size:';
        var input = document.createElement("input");
        input.id = "vector_size";
        input.min = "50";
        input.max = "300";
        input.defaultValue = "200";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        div.innerHTML += 'Window size:';
        var input = document.createElement("input");
        input.id = "window_size";
        input.min = "2";
        input.defaultValue = "10";
        input.max = "15";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        form_sidebar.appendChild(div);
        var div = document.createElement("div");
        div.style.fontSize = "13px";
        div.className = "nav-link";
        div.style.color = "#85b6fe";
        div.innerHTML += 'Min count:';
        var input = document.createElement("input");
        input.id = "min_count";
        input.min = "2";
        input.defaultValue = "2";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        div.innerHTML += 'Iterations:';
        var input = document.createElement("input");
        input.id = "iterations";
        input.min = "5";
        input.defaultValue = "25";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        form_sidebar.appendChild(div);

        var div = document.createElement("div");
        div.style.fontSize = "13px";
        div.className = "nav-link";
        div.style.color = "#85b6fe";
        div.innerHTML += 'Learning rate:';
        var input = document.createElement("input");
        input.id = "lr";
        input.min = "0.01";
        input.defaultValue = "0.05";
        input.max = "1";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        div.innerHTML += 'Alpha:';
        var input = document.createElement("input");
        input.id = "alpha";
        input.min = "0.75";
        input.defaultValue = "0.01";
        input.max = "1";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        form_sidebar.appendChild(div);
        var div = document.createElement("div");
        div.style.fontSize = "13px";
        div.className = "nav-link";
        div.style.color = "#85b6fe";
        div.innerHTML += 'x max:';
        var input = document.createElement("input");
        input.id = "x_max";
        input.defaultValue = "100";
        input.type = "number";
        input.style.cssText = 'margin-left: 5px; margin-right:20px; width: 50px; background-color: #343a40; color: rgba(255, 255, 255, 0.5); border: none;';
        div.appendChild(input);
        form_sidebar.appendChild(div);

        var div = document.createElement("div");
        div.className = "nav-link";
        div.style.marginTop = "10px";
        var button = document.createElement("button");
        button.id = "compute_glove_button";
        button.className = "button-4";
        button.role = "button";
        button.style.margin = "auto";
        button.innerHTML = "Compute";
        button.addEventListener("click", compute_glove_click);
        div.appendChild(button);
        form_sidebar.appendChild(div);

    }
};


//Create w2v after click compute button
const compute_w2v_click = (event) => {
    event.preventDefault();
    //vector_size, window_size, min_count <-ids 
    var check_text = document.getElementById("corpus_file").value.slice(-".txt".length) != ".txt";
    if (check_text) {
        alert("Choose a file '.txt'")
        event.target.value = null;
        return;
    };

    loading.style.visibility = 'visible';

    $.ajax({
        type: 'POST',
        url: '/compute_w2v',
        data: JSON.stringify({
            'path': document.getElementById("corpus_file").value,
            'vector_size': document.getElementById("vector_size").value,
            'window_size': document.getElementById('window_size').value,
            'min_count': document.getElementById("min_count").value
        }),
        success: function (data) {
            wordEmbeddings.push(data);
            var div2 = document.createElement("div");
            div2.className = "cat action";
            var img = document.createElement("img");
            img.className = "sb-nav-link-icon";
            img.src = "static/assets/embed.png";
            img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
            div2.appendChild(img);
            var label = document.createElement("label");
            label.style.verticalAlign = "middle";
            var input = document.createElement("input");
            input.type = "checkbox";
            input.id = data['name'];
            input.addEventListener("click", check_word_embedding_loaded);
            label.appendChild(input);
            var span = document.createElement("span");
            span.innerHTML += data['name'] + ": n_words=" + data['num_words'] + ", vec_size=" + data['vector_size'];
            label.appendChild(span);
            div2.appendChild(label);
            word_embeddings_loaded.appendChild(div2);
            while (form_sidebar.firstChild) {
                form_sidebar.removeChild(form_sidebar.firstChild);
            }
            upload.value = "";
            add_option_we_selections(data['name'], data['num_words'], data['vector_size']);
            loading.style.visibility = 'hidden';
        },
        error: function (error) {
            console.log(error);
            loading.style.visibility = 'hidden';
            alert("Error computing word2vec.")
        },
        contentType: "application/json",
        dataType: 'json'
    });


};


//Create glove after click compute button
const compute_glove_click = (event) => {
    event.preventDefault();
    //vector_size, window_size, min_count, iterations, lr, alpha, x_max<-ids
    var check_text = document.getElementById("corpus_file").value.slice(-".txt".length) != ".txt";
    if (check_text) {
        alert("Choose a file '.txt'")
        event.target.value = null;
        return;
    };

    loading.style.visibility = 'visible';

    $.ajax({
        type: 'POST',
        url: '/compute_glove',
        data: JSON.stringify({
            'path': document.getElementById("corpus_file").value,
            'vector_size': document.getElementById("vector_size").value,
            'window_size': document.getElementById('window_size').value,
            'min_count': document.getElementById("min_count").value,
            'iterations': document.getElementById("iterations").value,
            'lr': document.getElementById("lr").value,
            'alpha': document.getElementById("alpha").value,
            'x_max': document.getElementById("x_max").value,
        }),
        success: function (data) {
            wordEmbeddings.push(data);
            var div = document.getElementById("word_embeddings_loaded");
            var div2 = document.createElement("div");
            div2.className = "cat action";
            var img = document.createElement("img");
            img.className = "sb-nav-link-icon";
            img.src = "static/assets/embed.png";
            img.style.cssText = "width:15px; height:15px; margin-right: 0.5rem;";
            div2.appendChild(img);
            var label = document.createElement("label");
            label.style.verticalAlign = "middle";
            var input = document.createElement("input");
            input.type = "checkbox";
            input.id = data['name'];
            input.addEventListener("click", check_word_embedding_loaded);
            label.appendChild(input);
            var span = document.createElement("span");
            span.innerHTML += data['name'] + ": n_words=" + data['num_words'] + ", vec_size=" + data['vector_size'];
            label.appendChild(span);
            div2.appendChild(label);
            div.appendChild(div2);
            while (form_sidebar.firstChild) {
                form_sidebar.removeChild(form_sidebar.firstChild);
            }
            upload.value = "";
            add_option_we_selections(data['name'], data['num_words'], data['vector_size']);
            loading.style.visibility = 'hidden';
        },
        error: function (error) {
            console.log(error);
            loading.style.visibility = 'hidden';
            alert("Error computing glove.")
        },
        contentType: "application/json",
        dataType: 'json'
    });
};



