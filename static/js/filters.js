const elements = document.getElementsByTagName("input")
const title_or_description = document.getElementById("title_or_description")
const lower_price = document.getElementById("lower_price")
const upper_price = document.getElementById("upper_price")
const rangeSlider = document.querySelector(".range-slider")
clearInputs = () => {
  title_or_description.value = ""
  lower_price.value = "50"
  upper_price.value = "3000"
  rangeSlider["data-start-min"] = "50"
  for (var i = 0; i < elements.length; i++) {
    if (elements[i].type == "radio") {
      elements[i].checked = false
    }
  }
  window.location.href = "/"
}
