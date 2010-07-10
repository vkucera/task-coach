    //
//  TaskDetailsRecurrenceControlleriPad.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskCoachAppDelegate.h"
#import "TaskDetailsRecurrenceControlleriPad.h"
#import "CDTask.h"
#import "CDTask+Addons.h"
#import "CDDomainObject+Addons.h"
#import "i18n.h"

@implementation TaskDetailsRecurrenceControlleriPad

@synthesize mainLabel, recurrenceSwitch, amountField, periodButton, sameWeekdayLabel, sameWeekdaySwitch;

- initWithTask:(CDTask *)theTask
{
	if ((self = [super initWithNibName:@"TaskDetailsRecurrenceControlleriPad" bundle:[NSBundle mainBundle]]))
	{
		task = [theTask retain];
	}

	return self;
}

- (void)update
{
	[recurrenceSwitch setOn:task.recPeriod != nil];
	if (task.recPeriod != nil)
	{
		amountField.text = [NSString stringWithFormat:@"%@", task.recRepeat];
		amountField.hidden = NO;
		switch ([task.recPeriod intValue])
		{
			case REC_DAILY:
				[periodButton setTitle:_("Day(s)") forState:UIControlStateNormal];
				break;
			case REC_WEEKLY:
				[periodButton setTitle:_("Week(s)") forState:UIControlStateNormal];
				break;
			case REC_MONTHLY:
				[periodButton setTitle:_("Month(s)") forState:UIControlStateNormal];
				break;
			case REC_YEARLY:
				[periodButton setTitle:_("Year(s)") forState:UIControlStateNormal];
				break;
		}
		periodButton.hidden = NO;
		
		switch ([task.recPeriod intValue])
		{
			case REC_MONTHLY:
			case REC_YEARLY:
				sameWeekdayLabel.hidden = NO;
				[sameWeekdaySwitch setOn:[task.recSameWeekday intValue]];
				sameWeekdaySwitch.hidden = NO;
				break;
			default:
				sameWeekdayLabel.hidden = YES;
				sameWeekdaySwitch.hidden = YES;
				break;
		}
	}
	else
	{
		amountField.hidden = YES;
		periodButton.hidden = YES;
		sameWeekdayLabel.hidden = YES;
		sameWeekdaySwitch.hidden = YES;
	}
}

- (void)viewDidLoad
{
	[super viewDidLoad];
	[self update];

	mainLabel.text = _("Recurrence");
	sameWeekdayLabel.text = _("Same weekday");
}

- (void)viewDidUnload
{
	self.recurrenceSwitch = nil;
	self.amountField = nil;
	self.periodButton = nil;
	self.sameWeekdayLabel = nil;
	self.sameWeekdaySwitch = nil;
}

- (void)dealloc
{
	[self viewDidUnload];

	[task release];

    [super dealloc];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    return YES;
}

#pragma mark Actions

- (void)save
{
	[task markDirty];
	[task save];
}

- (IBAction)onRecurrenceChanged:(UISwitch *)_switch;
{
	if (_switch.on)
	{
		task.recPeriod = [NSNumber numberWithInt:REC_DAILY];
		task.recRepeat = [NSNumber numberWithInt:1];
		[amountField becomeFirstResponder];
	}
	else
	{
		task.recPeriod = nil;

		if ([amountField isFirstResponder])
			[amountField resignFirstResponder];
	}

	[self save];

	[self update];
}

- (IBAction)onPeriodChanged:(UIButton *)button
{
	NSInteger p = [task.recPeriod intValue];
	p = (p + 1) % 4;
	task.recPeriod = [NSNumber numberWithInt:p];
	[self save];
	[self update];
}

- (IBAction)onSameWeekdayChanged:(UISwitch *)_switch
{
	task.recSameWeekday = [NSNumber numberWithInt:_switch.on];
	[self save];
}

#pragma mark UIAlertViewDelegate

- (void)alertView:(UIAlertView *)alertView didDismissWithButtonIndex:(NSInteger)buttonIndex
{
}

#pragma mark UITextFieldDelegate

- (BOOL)textField:(UITextField *)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString *)string
{
	NSString *newValue = [textField.text stringByReplacingCharactersInRange:range withString:string];
	if ([newValue length])
	{
		task.recRepeat = [NSNumber numberWithInt:atoi([newValue UTF8String])];
	}
	else
	{
		task.recRepeat = [NSNumber numberWithInt:1];
	}

	[self save];

	return YES;
}

@end
