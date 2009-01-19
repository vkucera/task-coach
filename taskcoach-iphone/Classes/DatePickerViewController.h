//
//  DatePickerViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface DatePickerViewController : UIViewController
{
	UIDatePicker *picker;
	NSDate *date;
	
	id target;
	SEL action;
}

@property (nonatomic, retain) IBOutlet UIDatePicker *picker;

- (IBAction)onConfirm:(UIButton *)button;
- (IBAction)onCancel:(UIButton *)button;

- initWithDate:(NSString *)date target:(id)target action:(SEL)action;

@end
