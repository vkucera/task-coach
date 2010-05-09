//
//  DatePickerViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "DatePickerViewController.h"
#import "DateUtils.h"
#import "NSDate+Utils.h"

@implementation DatePickerViewController

@synthesize picker;

- initWithDate:(NSString *)theDate target:(id)theTarget action:(SEL)theAction
{
	if (self = [super initWithNibName:@"DatePickerView" bundle:[NSBundle mainBundle]])
	{
		target = theTarget;
		action = theAction;

		if (theDate)
		{
			date = [[[TimeUtils instance] dateFromString:theDate] retain];
		}
		else
		{
			date = [[NSDate dateRounded] retain];
		}
		
		dayFormat = [[NSDateFormatter alloc] init];
		[dayFormat setDateFormat:@"EEEE"];
	}

	return self;
}

- (void)viewDidLoad
{
	picker.date = date;
}

- (void)viewDidUnload
{
	self.picker = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[dayFormat release];
	[date release];
	
	[super dealloc];
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
