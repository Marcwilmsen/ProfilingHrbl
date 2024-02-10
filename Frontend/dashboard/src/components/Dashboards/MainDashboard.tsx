import React from "react";

class MainDashboard extends React.Component {
	render() {
		return (
			<div>
				<iframe
					src="https://grafana.sod3.eu/public-dashboards/eddf74871c47438a8a0138d2486e6809"
					width="100%"
					height="1050"
					title="Grafana Dashboard"
				></iframe>
			</div>
		);
	}
}

export default MainDashboard;
