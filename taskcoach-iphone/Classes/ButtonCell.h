//
//  ButtonCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 27/12/09.
//  Copyright 2009 Jérôme Laheurte. All rights reserved.
//

#import <UIKit/UIKit.h>


@interface ButtonCell : UITableViewCell
{
	UIButton *button;
	id target;
	SEL action;
}

@property (nonatomic, retain) IBOutlet UIButton *button;

- (void)setTarget:(id)target action:(SEL)action;

- (IBAction)onClicked:(UIButton *)btn;

@end
