//
//  RecurrencePeriodCell.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 12/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "RecurrencePeriodCell.h"

@implementation RecurrencePeriodCell

@synthesize textField;
@synthesize label;

- (void)setDelegate:(id <RecurrencePeriodCellDelegate>)theDelegate
{
	delegate = theDelegate;
}

- (BOOL)textField:(UITextField *)theTextField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString *)string
{
	NSString *newValue = [textField.text stringByReplacingCharactersInRange:range withString:string];

	if ([newValue length])
		[delegate recurrencePeriodCell:self valueDidChange:atoi([newValue UTF8String])];
	else
		[delegate recurrencePeriodCell:self valueDidChange:0];

	return YES;
}

@end
