copyText = async (link) => {
  try {
    await navigator.clipboard.writeText(link)
    const success_alert__container = document.getElementById("success_alert__container")
    success_alert__container.classList.remove("d-none")
    success_alert__container.classList.add("d-block")
  } catch (err) {
    console.log(err)
  }
}
