//
//  TextFieldCell.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>


@interface TextFieldCell : UITableViewCell
{
	UITextField *textField;
}

@property (nonatomic, retain) IBOutlet UITextField *textField;

@end
