//
//  DatePickerViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

@interface DatePickerViewController : UIViewController
{
	UIDatePicker *picker;
	UILabel *dayLabel;
	NSDate *date;
	
	id target;
	SEL action;
	
	NSDateFormatter *dayFormat;
}

@property (nonatomic, retain) IBOutlet UIDatePicker *picker;
@property (nonatomic, retain) IBOutlet UILabel *dayLabel;

- (IBAction)onDateChanged:(UIDatePicker *)picker;
- (IBAction)onConfirm:(UIButton *)button;
- (IBAction)onCancel:(UIButton *)button;

- initWithDate:(NSString *)date target:(id)target action:(SEL)action;

@end