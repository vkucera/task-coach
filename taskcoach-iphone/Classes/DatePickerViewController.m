//
//  DatePickerViewController.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import "DatePickerViewController.h"
#import "NSDate+Utils.h"

@implementation DatePickerViewController

@synthesize picker;

- initWithDate:(NSDate *)theDate target:(id)theTarget action:(SEL)theAction
{
	if ((self = [super initWithNibName:@"DatePickerView" bundle:[NSBundle mainBundle]]))
	{
		[self setDate:theDate target:theTarget action:theAction];
	}

	return self;
}

- (void)setDate:(NSDate *)theDate target:(id)theTarget action:(SEL)theAction
{
	target = theTarget;
	action = theAction;

	[date release];

	if (theDate)
	{
		date = [theDate retain];
	}
	else
	{
		date = [[NSDate dateRounded] retain];
	}

	[self.picker setDate:date animated:NO];
}

- (void)viewDidLoad
{
	self.picker.date = date;
}

- (void)viewDidUnload
{
	self.picker = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

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
