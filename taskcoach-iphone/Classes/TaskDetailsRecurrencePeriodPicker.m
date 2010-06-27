//
//  TaskDetailsRecurrencePeriodPicker.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 12/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskDetailsRecurrencePeriodPicker.h"
#import "i18n.h"
#import "CDTask+Addons.h"

@implementation TaskDetailsRecurrencePeriodPicker

@synthesize picker;

- init
{
	if ((self = [super initWithNibName:@"TaskDetailsRecurrencePeriodPicker" bundle:[NSBundle mainBundle]]))
	{
	}

	return self;
}

- (void)dealloc
{
	self.picker = nil;

    [super dealloc];
}

- (void)setDelegate:(id <TaskDetailsRecurrencePeriodPickerDelegate>)theDelegate
{
	delegate = theDelegate;
}

- (void)setSelection:(NSInteger)sel
{
	[picker selectRow:sel inComponent:0 animated:NO];
}

- (IBAction)onCancel:(UIButton *)button
{
	[delegate recurrencePeriodPickerdidCancel:self];
}

- (IBAction)onConfirm:(UIButton *)button
{
	[delegate recurrencePeriodPicker:self didConfirm:[picker selectedRowInComponent:0]];
}

#pragma mark UIPickerView

- (NSInteger)numberOfComponentsInPickerView:(UIPickerView *)pickerView
{
	return 1;
}

- (NSInteger)pickerView:(UIPickerView *)pickerView numberOfRowsInComponent:(NSInteger)component
{
	return 4;
}

- (NSString *)pickerView:(UIPickerView *)pickerView titleForRow:(NSInteger)row forComponent:(NSInteger)component
{
	switch (row)
	{
		case REC_DAILY:
			return _("Daily");
		case REC_WEEKLY:
			return _("Weekly");
		case REC_MONTHLY:
			return _("Monthly");
		case REC_YEARLY:
			return _("Yearly");
	}

	return nil;
}

@end
