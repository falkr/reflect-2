const mockUnits = [
	{
		hidden: false,
		title: 'State Machines',
		date_available: '2022-08-23',
		course_id: 'TDT4100',
		course_semester: 'fall2023',
		id: 1,
		reflections: [],
		unit_number: 1
	},
	{
		hidden: false,
		title: 'HTTP og JSON',
		date_available: '2022-08-30',
		course_id: 'TDT4100',
		course_semester: 'fall2023',
		id: 2,
		reflections: [],
		unit_number: 2
	},
	{
		hidden: false,
		title: 'MQTT Chat',
		date_available: '2024-09-07',
		course_id: 'TDT4100',
		course_semester: 'fall2023',
		id: 3,
		reflections: [],
		unit_number: 3
	}
];

const mockUnit = {
	unit: {
		hidden: false,
		title: 'asdasd',
		date_available: '2024-04-12',
		course_id: 'QWE213',
		course_semester: 'spring2024',
		id: 5,
		reflections: []
	},
	unit_questions: [
		{
			id: 5,
			question: 'Teaching',
			comment: 'What was your best learning success in this unit? Why?'
		},
		{
			id: 6,
			question: 'Difficult',
			comment: 'What was your least understood concept in this unit? Why?'
		}
	]
};

const mockUnitId = 5;

const mockUser = {
	uid: 'test',
	email: 'test@ntnu.no',
	enrollments: [
		{
			course_id: 'TDT4000',
			course_semester: 'spring2024',
			role: 'lecturer',
			uid: 'test',
			missingUnits: []
		},
		{
			course_id: 'TDT4100',
			course_semester: 'fall2023',
			role: 'student',
			uid: 'test',
			missingUnits: [
				{
					id: 1,
					date: '2022-08-23'
				},
				{
					id: 2,
					date: '2022-08-30'
				}
			]
		}
	],
	reflections: [],
	admin: true
};

const mockCourse = {
	id: 'TDT4100',
	semester: 'fall2023',
	name: 'Informasjonsteknologi grunnkurs',
	responsible: '',
	website: '',
	questions: [
		{
			id: 1,
			question: 'Teaching',
			comment: 'What was your best learning success in this unit? Why?'
		},
		{
			id: 2,
			question: 'Difficult',
			comment: 'What was your least understood concept in this unit? Why?'
		}
	],
	users: [
		{
			course_id: 'TDT4100',
			course_semester: 'fall2023',
			role: 'student'
		}
	],
	reports: [
		{
			report_content: [],
			number_of_answers: 0,
			unit_id: 1,
			course_id: 'TDT4100',
			course_semester: 'fall2023'
		},
		{
			report_content: [],
			number_of_answers: 0,
			unit_id: 2,
			course_id: 'TDT4100',
			course_semester: 'fall2023'
		},
		{
			report_content: [],
			number_of_answers: 0,
			unit_id: 3,
			course_id: 'TDT4100',
			course_semester: 'fall2023'
		}
	]
};

const mockData = [
	{
		user: mockUser,
		course: mockCourse,
		course_name: 'TDT4100',
		role: 'student',
		units: mockUnits,
		unit: mockUnit,
		unit_id: mockUnitId
	}
];
module.exports = {
	mockData,
	mockUnits,
	mockUnit,
	mockUnitId,
	mockCourse,
	mockUser
};
