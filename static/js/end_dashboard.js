// Line Chart of no.of endorsers, staff and earnings
const lineChart = document.getElementById("lineChart")
new Chart(lineChart, {
  type: "line",
  data: {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: [
      {
        label: "Organizations",
        data: [65, 59, 80, 81, 56, 55, 40],
        fill: false,
        borderColor: "rgb(253, 86, 49)",
        tension: 0.1,
      },
      {
        label: "Orders",
        data: [6, 5, 45, 15, 10, 30, 25],
        fill: false,
        borderColor: "rgb(255, 205, 86)",
        tension: 0.1,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  },
})

// Doughnut Chart of Earnings
const doughnutChart = document.getElementById("doughnutChart")
new Chart(doughnutChart, {
  type: "doughnut",
  data: {
    labels: ["January", "February", "March", "April", "May", "June", "July"],
    datasets: [
      {
        label: "Earnings",
        data: [65, 59, 80, 81, 56, 55, 40],
        backgroundColor: [
          "rgb(255, 99, 132)", // January
          "rgb(54, 162, 235)", // Febraury
          "rgb(255, 205, 86)", // March
          "rgb(255, 85, 125)", // April
          "rgb(78, 178, 200)", // May
          "rgb(189, 25, 148)", // June
          "rgb(198, 108, 98)", // July
        ],
        hoverOffset: 4,
      },
    ],
  },
})
