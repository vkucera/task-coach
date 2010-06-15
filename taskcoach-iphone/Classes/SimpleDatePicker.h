//
//  SimpleDatePicker.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 15/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface SimpleDatePicker : UIViewController
{
	UIDatePicker *picker;
	id target;
	SEL action;
}

@property (nonatomic, retain) IBOutlet UIDatePicker *picker;
@property (nonatomic, retain) NSDate *date;

- initWithTarget:(id)target action:(SEL)action;

- (IBAction)onClickNone:(UIButton *)button;

@end
