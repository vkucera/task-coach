//
//  DatePickerViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "DatePickerViewController.h"
#import "DateUtils.h"

@implementation DatePickerViewController

@synthesize picker;
@synthesize dayLabel;

- initWithDate:(NSString *)theDate target:(id)theTarget action:(SEL)theAction
{
	if (self = [super initWithNibName:@"DatePickerView" bundle:[NSBundle mainBundle]])
	{
		target = theTarget;
		action = theAction;

		if (theDate)
		{
			date = [[DateUtils instance] dateFromString:theDate];
		}
		else
		{
			date = [NSDate date];
		}
		
		dayFormat = [[NSDateFormatter alloc] init];
		[dayFormat setDateFormat:@"EEEE"];
	}

	return self;
}

- (void)dealloc
{
	[picker release];
	[dayLabel release];
	[dayFormat release];

	[super dealloc];
}

- (void)viewDidLoad
{
	picker.date = date;
	dayLabel.text = [dayFormat stringFromDate:date];
}

- (IBAction)onDateChanged:(UIDatePicker *)thePicker
{
	dayLabel.text = [dayFormat stringFromDate:thePicker.date];
}

- (IBAction)onConfirm:(UIButton *)button
{
	[target performSelector:action withObject:picker.date];
}

- (IBAction)onCancel:(UIButton *)button
{
	[target performSelector:action withObject:nil];
}

@end
