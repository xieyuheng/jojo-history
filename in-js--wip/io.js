function get_element (id)
{
    return document.getElementById (id);
}

let input_buffer  = get_element ("input_buffer");
let output_buffer = get_element ("output_buffer");

input_buffer.focus ();

input_buffer.onkeydown = function (event)
{
    if (event.key === "F2") {
        let input = input_buffer.value;
        let output = "";
        output = output.concat (input);
        output_buffer.value = output;
        input_buffer.focus ();
    }
};
